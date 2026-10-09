from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload
from app.common.exceptions import BusinessException
from app.common.response import QueryResponse
from app.model.equipment import Equipment
from app.model.lab import Lab
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.equipment import (
    EquipmentCreateRequest,
    EquipmentResponse,
    EquipmentUpdateRequest,
)


# 查询实验室设备列表
async def get_equipment_list_service(
    db: AsyncSession,
    page: int,
    page_size: int,
    keyword: str | None = None,
    lab_id: int | None = None,
) -> QueryResponse:

    # 跳过多少条数据
    skip = (page - 1) * page_size
    stmt = (
        select(Equipment)
        .options(selectinload(Equipment.lab))
        .order_by(Equipment.id.asc())
        .offset(skip)
        .limit(page_size)
    )
    count_stmt = select(func.count(Equipment.id))
    if lab_id is not None:
        stmt = stmt.where(Equipment.lab_id == lab_id)
        count_stmt = count_stmt.where(Equipment.lab_id == lab_id)
    if keyword:
        stmt = stmt.join(Equipment.lab)
        count_stmt = count_stmt.join(Equipment.lab)
        condition = or_(
            Equipment.name.contains(keyword),
            Lab.name.contains(keyword),
        )
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)
    query = await db.execute(stmt)
    equipments = query.scalars().all()
    total = await db.execute(count_stmt)
    return QueryResponse(
        items=[EquipmentResponse.model_validate(equipment) for equipment in equipments],
        total=total.scalar(),
    )


# 管理员创建实验室设备
async def Create_equipment_service(data: EquipmentCreateRequest, db: AsyncSession):
    """管理员创建实验室设备"""

    # 判断实验室名是否存在
    equipment = (
        await db.execute(select(Equipment).where(Equipment.name == data.name))
    ).scalar_one_or_none()
    if equipment:
        raise BusinessException(message="实验室设备已存在")
    equipment = Equipment()
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(equipment, k, v)
    db.add(equipment)
    await db.commit()
    await db.refresh(equipment, ["lab"])
    return EquipmentResponse.model_validate(equipment)


# 管理员更新实验室设备信息
async def Update_equipment_service(
    equipment_id: int, data: EquipmentUpdateRequest, db: AsyncSession
) -> EquipmentResponse:
    """管理员更新实验室设备信息"""

    # 判断实验室是否存在
    equipment = (
        await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    ).scalar_one_or_none()
    if not equipment:
        raise BusinessException(message="实验室设备不存在")

    equipment_dict = data.model_dump(exclude_unset=True)
    # pydantic 转换为字典

    for k, v in equipment_dict.items():
        setattr(equipment, k, v)
    await db.commit()
    await db.refresh(equipment, ["lab"])
    return EquipmentResponse.model_validate(equipment)


# 删除实验室设备
async def Delete_equipment_service(equipment_id: int, db: AsyncSession) -> None:
    """删除实验室设备"""

    # 判断实验室设备是否存在
    equipment = (
        await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    ).scalar_one_or_none()
    if not equipment:
        raise BusinessException(message="实验室设备不存在")

    await db.delete(equipment)
    await db.commit()
    return None
