# 用户模块的请求和响应模型
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    name: str
    role: str
    status: int
    email: str | None = None
    phone: str | None = None
    avatar: str | None = None
    create_time: datetime
    update_time: datetime


class UserUpdateRequest(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    avatar: str | None = None
    role: str | None = None
    status: int = 1


class UserPasswordUpdateRequest(BaseModel):
    old_password: str
    new_password: str


class UserCreateRequest(BaseModel):
    username: str
    password: str = "123"
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    avatar: str | None = None
    role: str = "学生"
    status: int = 1
