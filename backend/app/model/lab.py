from app.database import Base
from sqlalchemy import Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column
from datetime import time


class Lab(Base):
    __tablename__ = "lab"
    __table_args__ = {"comment": "实验室表"}

    name: Mapped[str] = mapped_column(String(50), comment="实验室名称")
    location: Mapped[str | None] = mapped_column(String(100), comment="位置")
    capacity: Mapped[int] = mapped_column(Integer, comment="容纳人数", default=0)
    open_time: Mapped[time | None] = mapped_column(Time, comment="开放开始时间")
    close_time: Mapped[time | None] = mapped_column(Time, comment="开放结束时间")
    description: Mapped[str | None] = mapped_column(String(500), comment="简介")
    img: Mapped[str | None] = mapped_column(String(255), comment="封面图")
    status: Mapped[int] = mapped_column(default=1, comment="状态: 0-关闭, 1-开放")
