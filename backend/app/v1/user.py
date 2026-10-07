from fastapi import APIRouter, Depends
from app.model.user import User
from app.dependencies.auth import get_current_user, judge_manager
from app.common.response import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import (
    UserCreateRequest,
    UserPasswordUpdateRequest,
    UserUpdateRequest,
)
from app.database import get_async_session
from typing import Annotated
from app.server.user_service import (
    Create_user_service,
    Delete_user_service,
    Update_user_service,
    get_user_info_service,
    get_user_list_service,
    update_user_info_service,
    update_user_password_service,
)


router = APIRouter(prefix="/user", tags=["用户信息接口"])


# 获取用户信息
@router.get("/info")
async def GetUserInfo(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return Response.success(data=get_user_info_service(current_user))


# 更新用户信息
@router.put("/update")
async def UpdateUserInfo(
    current_user: Annotated[User, Depends(get_current_user)],
    data: UserUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    """更新当前登录用户信息"""
    res = await update_user_info_service(current_user, data, db)
    return Response.success(data=res)


# 修改密码
@router.put("/password")
async def UpdateUserPassword(
    current_user: Annotated[User, Depends(get_current_user)],
    data: UserPasswordUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    """修改当前登录用户密码"""
    await update_user_password_service(current_user, data, db)
    return Response.success(message="密码修改成功")


# 查询用户列表
@router.get("/list")
async def GetUserList(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_manager: Annotated[User, Depends(judge_manager)],
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
):
    """查询用户列表"""
    res = await get_user_list_service(db, page, page_size, keyword)
    return Response.success(data=res)


# 管理员创建用户
@router.post("")
async def CreateUser(
    current_manager: Annotated[User, Depends(judge_manager)],
    data: UserCreateRequest,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    """管理员创建用户"""
    res = await Create_user_service(data, db)
    return Response.success(message="用户创建成功", data=res)


# 管理员更新用户
@router.put("/{userid}")
async def UpdateUser(
    current_manager: Annotated[User, Depends(judge_manager)],
    data: UserUpdateRequest,
    userid: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    """管理员更新用户"""
    res = await Update_user_service(userid, data, db)
    return Response.success(message="用户更新成功", data=res)


# 管理员删除用户
@router.delete("/{userid}")
async def DeleteUser(
    current_manager: Annotated[User, Depends(judge_manager)],
    userid: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    """管理员删除用户"""
    await Delete_user_service(userid, current_manager, db=db)
    return Response.success(message="用户删除成功")
