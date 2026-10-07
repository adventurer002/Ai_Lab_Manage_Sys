# 认证模块的路由
from fastapi import APIRouter, Depends
from app.database import get_async_session
from app.schemas.auth import LoginRequest, RegisterRequest
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.server.auth import login_judge, register_judge

from app.common.response import Response


router = APIRouter(prefix="/auth", tags=["权限认证"])


# 登录接口认证
@router.post("/login")
async def login(
    data: LoginRequest, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    # 根据用户名查询数据库中的用户
    result = await login_judge(data, db)
    return Response.success(data=result)


# 注册接口认证
@router.post("/register")
async def register(
    data: RegisterRequest, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    # 根据用户名查询数据库中的用户
    await register_judge(data, db)
    print("注册成功")
    return Response.success(message="注册成功")
