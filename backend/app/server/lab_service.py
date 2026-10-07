from sqlalchemy import func, select
from app.common.exceptions import BusinessException
from app.common.response import QueryResponse
from app.model.lab import Lab
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.lab import (
    LabCreateRequest,
    LabResponse,
    LabUpdateRequest,
)


# 查询实验室列表
async def get_lab_list_service(
    db: AsyncSession, page: int, page_size: int, keyword: str | None = None
) -> QueryResponse:

    # 跳过多少条数据
    skip = (page - 1) * page_size
    stmt = select(Lab).order_by(Lab.id.asc()).offset(skip).limit(page_size)
    count_stmt = select(func.count(Lab.id))
    if keyword:
        condition = Lab.name.contains(keyword)
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)
    query = await db.execute(stmt)
    labs = query.scalars().all()
    total = await db.execute(count_stmt)
    return QueryResponse(
        items=[LabResponse.model_validate(lab) for lab in labs],
        total=total.scalar(),
    )


# 管理员创建实验室
async def Create_lab_service(data: LabCreateRequest, db: AsyncSession):
    """管理员创建实验室"""

    # 判断实验室名是否存在
    lab = (
        await db.execute(select(Lab).where(Lab.name == data.name))
    ).scalar_one_or_none()
    if lab:
        raise BusinessException(message="实验室已存在")
    lab = Lab()
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(lab, k, v)
    db.add(lab)
    await db.commit()
    await db.refresh(lab)
    return LabResponse.model_validate(lab)


# 管理员更新实验室信息
async def Update_lab_service(
    lab_id: int, data: LabUpdateRequest, db: AsyncSession
) -> LabResponse:
    """管理员更新实验室信息"""

    # 判断实验室是否存在
    lab = (await db.execute(select(Lab).where(Lab.id == lab_id))).scalar_one_or_none()
    if not lab:
        raise BusinessException(message="实验室不存在")

    lab_dict = data.model_dump(exclude_unset=True)
    # pydantic 转换为字典

    for k, v in lab_dict.items():
        setattr(lab, k, v)
    await db.commit()
    await db.refresh(lab)
    return LabResponse.model_validate(lab)


# 删除实验室
async def Delete_lab_service(lab_id: int, db: AsyncSession) -> None:
    """删除实验室"""

    # 判断实验室是否存在
    lab = (await db.execute(select(Lab).where(Lab.id == lab_id))).scalar_one_or_none()
    if not lab:
        raise BusinessException(message="实验室不存在")

    await db.delete(lab)
    await db.commit()
    return None
