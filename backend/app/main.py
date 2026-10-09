import asyncio

from fastapi import FastAPI, HTTPException
from app.v1 import v1
from app.database import create_table, async_engine
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from app.common.exceptions import (
    BusinessException,
    bussiness_excpetion_hadler,
    http_excpetion_hadler,
    validation_excpetion_hadler,
    global_excpetion_hadler,
)
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.server.reservation_service import run_expire
from app.config import FILE_PATH


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_table()
    expire_task = asyncio.create_task(run_expire())
    yield
    expire_task.cancel()
    await async_engine.dispose()
    print("数据库引擎已关闭")


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的前端源，不要直接写 ["*"]
    allow_credentials=True,  # ✅ 关键：允许前端携带 Authorization token
    allow_methods=["*"],  # 允许所有请求方法 GET POST PUT DELETE OPTIONS
    allow_headers=["*"],  # 允许所有请求头（包含Authorization）
)

# 注册异常处理器
app.add_exception_handler(BusinessException, bussiness_excpetion_hadler)
app.add_exception_handler(HTTPException, http_excpetion_hadler)
app.add_exception_handler(RequestValidationError, validation_excpetion_hadler)
# 全局的异常兜底，必须放在最后注册！！
app.add_exception_handler(Exception, global_excpetion_hadler)

# 静态文件服务
app.mount("/uploads", StaticFiles(directory=FILE_PATH), name="uploads")

app.include_router(v1)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
