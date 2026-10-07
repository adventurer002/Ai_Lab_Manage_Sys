# 用户模块的请求和响应模型
from pydantic import BaseModel, ConfigDict
from datetime import datetime, time


class LabResponse(BaseModel):
    id: int
    name: str
    location: str | None = None
    capacity: int = 0
    open_time: time | None = None
    close_time: time | None = None
    description: str | None = None
    img: str | None = None
    status: int = 1

    # 开启模型属性的自动转换
    model_config = ConfigDict(from_attributes=True)


class LabCreateRequest(BaseModel):
    name: str
    location: str | None = None
    capacity: int = 0
    open_time: str | None = None
    close_time: str | None = None
    description: str | None = None
    img: str | None = None
    status: int = 1


class LabUpdateRequest(BaseModel):
    name: str | None = None
    location: str | None = None
    capacity: int | None = None
    open_time: str | None = None
    close_time: str | None = None
    description: str | None = None
    img: str | None = None
    status: int | None = None
