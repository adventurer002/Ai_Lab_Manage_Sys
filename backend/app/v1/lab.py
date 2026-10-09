from fastapi import APIRouter, Depends
from app.model.user import User
from app.dependencies.auth import get_current_user, judge_manager
from app.common.response import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.lab import LabCreateRequest, LabUpdateRequest

from app.database import get_async_session
from typing import Annotated
from app.server import lab_service
from app.server.lab_service import (
    Create_lab_service,
    Delete_lab_service,
    Update_lab_service,
    get_lab_list_service,
)


router = APIRouter(prefix="/lab", tags=["实验室信息接口"])


# 查询实验室列表
@router.get("/list")
async def GetLabList(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_manager: Annotated[User, Depends(get_current_user)],
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    status: int | None = None,
):
    """查询实验室列表"""
    res = await get_lab_list_service(db, page, page_size, keyword, status)
    return Response.success(message="查询实验室列表成功", data=res)


# 查询实验室详情
@router.get("/{lab_id}")
async def get_lab(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    lab_id: int,
    current_user: User = Depends(get_current_user),
):
    res = await lab_service.get_lab(db, lab_id)
    return Response.success(data=res)


# 管理员创建实验室
@router.post("")
async def CreateLab(
    current_manager: Annotated[User, Depends(judge_manager)],
    data: LabCreateRequest,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    """管理员创建实验室"""
    res = await Create_lab_service(data, db)
    return Response.success(message="实验室创建成功", data=res)


# 管理员更新实验室
@router.put("/{lab_id}")
async def UpdateLab(
    current_manager: Annotated[User, Depends(judge_manager)],
    data: LabUpdateRequest,
    lab_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    """管理员更新实验室"""
    res = await Update_lab_service(lab_id, data, db)
    return Response.success(message="实验室更新成功", data=res)


# 管理员删除实验室
@router.delete("/{lab_id}")
async def DeleteLab(
    current_manager: Annotated[User, Depends(judge_manager)],
    lab_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    """管理员删除实验室"""
    await Delete_lab_service(lab_id, db=db)
    return Response.success(message="实验室删除成功")
