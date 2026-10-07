# 创建数据库连接
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from datetime import datetime
from sqlalchemy import func, DateTime, String


from app.config import settings

# 创建异步数据库引擎
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # 打印sql日志
    future=True,  # 开启异步模式
    pool_size=10,
    max_overflow=20,
)


# 基础模型
class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="主键id"
    )
    create_time: Mapped[datetime] = mapped_column(
        default=func.now(), comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now(), comment="更新时间"
    )


# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


# 异步会话
async def get_async_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # 提交事务
            print("事务提交成功")
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
            print("会话已关闭")


# 创建数据库表
async def create_table():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("数据库表创建成功")
