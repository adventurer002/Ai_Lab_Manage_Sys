from sqlalchemy import func, select
from app.common.exceptions import BusinessException
from app.common.response import QueryResponse
from app.model.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import (
    UserCreateRequest,
    UserPasswordUpdateRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.utils.password import hash_password, verify_password


# 获取用户信息
def get_user_info_service(user: User) -> UserResponse:
    """获取用户信息"""
    return UserResponse.model_validate(user)


# 更新用户信息
async def update_user_info_service(
    user: User, data: UserUpdateRequest, db: AsyncSession
) -> UserResponse:
    """更新用户信息"""
    user_dict = data.model_dump(
        exclude_unset=True, exclude=["role", "status"]
    )  # pydantic 转换为字典
    for k, v in user_dict.items():
        setattr(user, k, v)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


# 修改密码
async def update_user_password_service(
    user: User, data: UserPasswordUpdateRequest, db: AsyncSession
) -> None:
    # 获取加密密码
    if not verify_password(data.old_password, user.password):
        raise BusinessException(message="原密码错误")
    elif data.old_password == data.new_password:
        raise BusinessException(message="新密码不能与原密码相同")
    else:
        user.password = hash_password(data.new_password)
        await db.commit()
        return None


# 查询用户列表
async def get_user_list_service(
    db: AsyncSession, page: int, page_size: int, keyword: str | None = None
) -> QueryResponse:

    # 跳过多少条数据
    skip = (page - 1) * page_size
    stmt = select(User).order_by(User.id.asc()).offset(skip).limit(page_size)
    count_stmt = select(func.count(User.id))
    if keyword:
        condition = User.username.contains(keyword) | User.name.contains(keyword)
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)
    query = await db.execute(stmt)
    users = query.scalars().all()
    total = await db.execute(count_stmt)
    return QueryResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total.scalar(),
    )


# 管理员创建用户
async def Create_user_service(data: UserCreateRequest, db: AsyncSession):
    """管理员创建用户"""

    # 判断用户名是否存在
    user = (
        await db.execute(select(User).where(User.username == data.username))
    ).scalar_one_or_none()
    if user:
        raise BusinessException(message="用户名已存在")

    user = User(
        username=data.username,
        password=hash_password(data.password),
        name=data.name,
        role=data.role,
        email=data.email,
        phone=data.phone,
        avatar=data.avatar,
        status=data.status,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


# 管理员更新用户信息
async def Update_user_service(
    userid: int, data: UserUpdateRequest, db: AsyncSession
) -> UserResponse:
    """管理员更新用户信息"""

    # 判断用户是否存在
    user = (
        await db.execute(select(User).where(User.id == userid))
    ).scalar_one_or_none()
    if not user:
        raise BusinessException(message="用户不存在")

    user_dict = data.model_dump(exclude_unset=True)  # pydantic 转换为字典
    for k, v in user_dict.items():
        setattr(user, k, v)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


# 删除用户
async def Delete_user_service(
    userid: int, current_user: User, db: AsyncSession
) -> None:
    """删除用户"""

    # 不能删除自己
    if userid == current_user.id:
        raise BusinessException(message="不能删除自己")

    # 判断用户是否存在
    user = (
        await db.execute(select(User).where(User.id == userid))
    ).scalar_one_or_none()
    if not user:
        raise BusinessException(message="用户不存在")

    # 管理员不能删除
    elif user.role == "管理员":
        raise BusinessException(message="管理员不能删除")

    await db.delete(user)
    await db.commit()
    return None
