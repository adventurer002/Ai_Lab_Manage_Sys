from app.database import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"comment": "用户表"}

    username: Mapped[str] = mapped_column(String(255), unique=True, comment="用户名")
    password: Mapped[str] = mapped_column(String(255), comment="密码")
    name: Mapped[str] = mapped_column(String(30), comment="姓名")
    role: Mapped[str] = mapped_column(String(30), comment="学生/教师/管理员")
    email: Mapped[str | None] = mapped_column(String(30), comment="邮箱")
    phone: Mapped[str | None] = mapped_column(String(30), comment="手机号")
    avatar: Mapped[str | None] = mapped_column(String(255), comment="头像")
    status: Mapped[int] = mapped_column(Integer, comment="状态")
