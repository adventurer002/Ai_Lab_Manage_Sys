from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.utils.password import verify_password
from app.utils.jwt import create_access_token
from app.utils.password import hash_password
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from app.schemas.user import UserResponse
from app.model.user import User
from app.common.exceptions import BusinessException


# 登录判断
async def login_judge(data: LoginRequest, db: AsyncSession) -> LoginResponse:
    user_result = await db.execute(select(User).where(User.username == data.username))
    user = user_result.scalar_one_or_none()
    if user is None or not verify_password(data.password, user.password):
        raise BusinessException("用户名或密码错误")
    if user.status != 1:
        raise BusinessException("用户已被禁用")
    token = create_access_token(user.id)
    return LoginResponse(token=token, user=UserResponse.model_validate(user))


# 注册判断
async def register_judge(data: RegisterRequest, db: AsyncSession) -> None:
    # 校验用户名是否存在
    user_result = await db.execute(select(User).where(User.username == data.username))
    exists = user_result.scalar_one_or_none()
    if exists:
        raise BusinessException("用户名已存在")
    # 校验密码是否为空
    elif not data.password or not data.username:
        raise BusinessException("用户名或密码不能为空")

    # 添加到数据库中
    user = User(
        username=data.username,
        password=hash_password(data.password),
        name=data.name or data.username,
        status=1,
        role="学生",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
