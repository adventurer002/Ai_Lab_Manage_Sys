import asyncio

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime, time
from app.common.exceptions import BusinessException
from app.common.response import QueryResponse
from app.database import AsyncSessionLocal
from app.model.equipment import Equipment
from app.model.lab import Lab
from app.model.reservation import Reservation
from app.model.user import User
from app.schemas.reservation import (
    ReservationCreateRequest,
    ReservationResponse,
)


async def create_reservation_service(
    db: AsyncSession, current_user: User, data: ReservationCreateRequest
):
    """创建预约记录"""
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")

    # 把前端传来的字符串时间转成 time 对象，便于和 Lab.open_time/close_time（Time 类型）比较
    start_time_obj = datetime.strptime(data.start_time, "%H:%M").time()
    end_time_obj = datetime.strptime(data.end_time, "%H:%M").time()

    # 1. 基础时效校验
    if data.date < current_date:
        raise BusinessException(message="预约日期不能小于当前的日期")
    if data.end_time <= data.start_time:
        raise BusinessException(message="预约的结束时间不能小于等于开始时间")
    if data.date == current_date and data.start_time <= current_time:
        raise BusinessException(message="预约开始时间不能小于等于当前的时间")

    # 2. 检查实验室（改用 select(...)，并用 scalar_one_or_none()）
    lab_res = await db.execute(select(Lab).where(Lab.id == data.lab_id))
    lab = lab_res.scalar_one_or_none()
    if lab is None:
        raise BusinessException(message="实验室不存在")
    if lab.status != 1:
        raise BusinessException(message="实验室已关闭")
    if lab.open_time and start_time_obj < lab.open_time:
        raise BusinessException(message="预约时间不能早于实验室的开放时间")
    if lab.close_time and end_time_obj > lab.close_time:
        raise BusinessException(message="预约时间不能晚于实验室的关闭时间")

    # 3. 检查设备（绑定实验室归属）
    if data.equipment_id:
        equip_res = await db.execute(
            select(Equipment).where(
                Equipment.id == data.equipment_id,
                Equipment.lab_id == data.lab_id,  # 确保设备归属于该实验室
            )
        )
        equipment = equip_res.scalar_one_or_none()
        if equipment is None:
            raise BusinessException(message="该实验室下不存在对应设备")
        if equipment.status != 1:
            raise BusinessException(message="实验室设备正在维修")

    # 4. 构建冲突检测查询（先组装，后执行）
    stmt = select(Reservation).where(
        Reservation.lab_id == data.lab_id,
        Reservation.date == data.date,
        Reservation.status.in_([0, 1]),  # 0待审核，1已通过
        Reservation.start_time < data.end_time,
        Reservation.end_time > data.start_time,
    )

    if data.equipment_id:
        # 约特定设备时：如果该设备已被约，或者整间实验室已被包场，均算冲突
        stmt = stmt.where(
            or_(
                Reservation.equipment_id == data.equipment_id,
                Reservation.equipment_id.is_(None),
            )
        )
    # else: 约整间实验室时无需加额外条件，该实验室只要有冲突记录就拦截

    conflict_res = await db.execute(stmt)
    if conflict_res.scalars().first() is not None:
        raise BusinessException(message="该时段已预约")

    # 5. 落库提交
    reservation_model = Reservation(
        user_id=current_user.id,
        lab_id=data.lab_id,
        equipment_id=data.equipment_id,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
        remark=data.remark,
        status=0,
    )
    db.add(reservation_model)
    await db.commit()
    await db.refresh(reservation_model)  # 获取自增ID等字段

    return reservation_model


# reserve list列表
async def get_reservation_list_service(
    db: AsyncSession,
    current_user: User,
    page: int,
    page_size: int,
    status: int | None = None,
):
    """获取预约记录列表"""

    stmt = select(Reservation)

    if current_user.role == "学生":
        stmt = stmt.where(Reservation.user_id == current_user.id)
    if status is not None:
        stmt = stmt.where(Reservation.status == status)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()
    if total == 0:
        return QueryResponse(items=[], total=0)

    items_stmt = (
        stmt.options(
            selectinload(Reservation.user),
            selectinload(Reservation.lab),
            selectinload(Reservation.equipment),
        )
        .order_by(Reservation.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(items_stmt)
    items = result.scalars().all()

    # 4. 组装响应数据
    item_list = []
    for item in items:
        res = ReservationResponse.model_validate(item)
        res.user_name = item.user.name if item.user else None
        res.lab_name = item.lab.name if item.lab else None
        res.equipment_name = item.equipment.name if item.equipment else None
        res.type = "设备" if item.equipment_id else "实验室"
        item_list.append(res)

    return QueryResponse(items=item_list, total=total)


# cancel cancel预约
async def cancel_reservation_service(
    db: AsyncSession, current_user: User, reservation_id: int
):
    """学生取消预约"""
    item_res = await db.execute(
        select(Reservation).where(Reservation.id == reservation_id)
    )
    item = item_res.scalar_one_or_none()
    if not item:
        raise BusinessException(message="预约记录不存在")
    if item.user_id != current_user.id:
        raise BusinessException(message="无权限", code=403)
    if item.status != 0:
        raise BusinessException(message="当前状态无法取消")
    item.status = 3
    await db.commit()
    await db.refresh(item)


# audit 审核预约


async def audit_reservation_service(db: AsyncSession, reservation_id: int, status: int):
    """管理员审核预约"""
    if status not in [1, 2]:
        raise BusinessException(message="审核状态错误")
    item_res = await db.execute(
        select(Reservation).where(Reservation.id == reservation_id)
    )
    item = item_res.scalar_one_or_none()
    if not item:
        raise BusinessException(message="预约记录不存在")
    if item.status != 0:
        raise BusinessException(message="当前状态不支持审核")
    item.status = status
    await db.commit()
    await db.refresh(item)


# 超时取消
async def expire_pending_reservation_service(db: AsyncSession):
    """超时取消预约"""
    try:
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M")
        Change = False
        items_res = await db.execute(
            select(Reservation).where(
                Reservation.status == 0,
            )
        )
        items = items_res.scalars().all()
        for item in items:
            if item.date < date or (item.date == date and item.end_time < time):
                item.status = 3
                Change = True
        if Change:
            await db.commit()
    finally:
        await db.close()


async def run_expire():
    """超时取消预约"""
    while True:
        try:
            async with AsyncSessionLocal() as db:
                await expire_pending_reservation_service(db)
        except Exception as e:
            print(e)
        await asyncio.sleep(60)
