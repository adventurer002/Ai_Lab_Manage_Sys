# 包含认证依赖项的模块
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from typing import Annotated
from app.utils.jwt import decode_access_token
from app.model.user import User
from sqlalchemy import select
from app.common.exceptions import BusinessException


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")  # 登录接口认证


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> User:
    """
    获取当前用户信息
    """
    # 验证token是否有效
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="登录过期，请重新登录"
        )

    # 查看usr_id
    usr_id = payload.get("usr_id")
    if not usr_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的登录凭证"
        )

    # 查询用户状态
    result = await db.execute(select(User).where(User.id == usr_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在"
        )

    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="用户已被禁用"
        )
    return user


# 管理用户依赖
async def judge_manager(user: Annotated[User, Depends(get_current_user)]):
    if user.role != "管理员":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="非管理员用户"
        )
    return user
