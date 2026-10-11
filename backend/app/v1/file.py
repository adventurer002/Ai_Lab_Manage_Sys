import asyncio
import os
import time
import uuid
from typing import Annotated

from anyio import Path
from fastapi import APIRouter, Depends, File, UploadFile

from app.common.exceptions import BusinessException
from app.common.response import Response
from app.config import ALLOWED_EXTENSIONS, FILE_PATH, MAX_FILE_SIZE
from app.dependencies.auth import get_current_user
from app.model.user import User

router = APIRouter(prefix="/file", tags=["文件接口"])


def _write_bytes(path, content: bytes) -> None:
    """同步写文件，供 asyncio.to_thread 在线程池中调用。"""
    with open(path, "wb") as f:
        f.write(content)


@router.post("/upload")
async def upload_file(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not file.filename:
        raise BusinessException("文件名不能为空")
    # 获取原始文件名
    original_filename = os.path.basename(file.filename)

    # 获取文件扩展名
    ext = Path(original_filename).suffix.lower()
    # 检查文件扩展名是否在允许的范围内
    if ext not in ALLOWED_EXTENSIONS:
        raise BusinessException(f"文件扩展名 {ext} 不被允许")
    # 检查文件大小是否超过最大允许大小
    if file.size and file.size > MAX_FILE_SIZE:
        raise BusinessException("文件大小不能超过100MB")

    # 加密文件名
    disk_name = f"{int(time.time()*1000)}_{uuid.uuid4().hex}{ext}"

    # 异步读取 + 线程池写盘，避免阻塞事件循环
    content = await file.read()
    await asyncio.to_thread(_write_bytes, FILE_PATH / disk_name, content)

    return Response.success(
        message="文件上传成功",
        data={
            "original_name": original_filename,
            "disk_name": disk_name,
            "size": file.size,
            "url": f"/uploads/{disk_name}",
        },
    )
