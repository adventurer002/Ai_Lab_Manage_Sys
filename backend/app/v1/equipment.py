from fastapi import APIRouter, Depends
from app.model.user import User
from app.dependencies.auth import judge_manager
from app.common.response import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.equipment import EquipmentCreateRequest, EquipmentUpdateRequest

from app.database import get_async_session
from typing import Annotated
from app.server.equipment_service import (
    Create_equipment_service,
    Delete_equipment_service,
    Update_equipment_service,
    get_equipment_list_service,
)


router = APIRouter(prefix="/equipment", tags=["实验室设备信息接口"])


# 查询实验室设备列表
@router.get("/list")
async def GetEquipmentList(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_manager: Annotated[User, Depends(judge_manager)],
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    lab_id: int | None = None,
):
    """查询实验室设备列表"""
    res = await get_equipment_list_service(db, page, page_size, keyword, lab_id)
    return Response.success(message="查询实验室设备列表成功", data=res)


# 管理员创建实验室设备
@router.post("")
async def CreateEquipment(
    current_manager: Annotated[User, Depends(judge_manager)],
    data: EquipmentCreateRequest,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    """管理员创建实验室设备"""
    res = await Create_equipment_service(data, db)
    return Response.success(message="实验室设备创建成功", data=res)


# 管理员更新实验室设备
@router.put("/{equipment_id}")
async def UpdateEquipment(
    current_manager: Annotated[User, Depends(judge_manager)],
    data: EquipmentUpdateRequest,
    equipment_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    """管理员更新实验室设备"""
    res = await Update_equipment_service(equipment_id, data, db)
    return Response.success(message="实验室设备更新成功", data=res)


# 管理员删除实验室设备
@router.delete("/{equipment_id}")
async def DeleteEquipment(
    current_manager: Annotated[User, Depends(judge_manager)],
    equipment_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    """管理员删除实验室设备"""
    await Delete_equipment_service(equipment_id, db=db)
    return Response.success(message="实验室设备删除成功")
