import shutil
import os
import time
import uuid
from anyio import Path
from app.common.exceptions import BusinessException
from fastapi import APIRouter, UploadFile, FastAPI, File
from app.common.response import Response
from app.config import MAX_FILE_SIZE, FILE_PATH, ALLOWED_EXTENSIONS

router = APIRouter(prefix="/file", tags=["文件接口"])


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
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

    with open(FILE_PATH / disk_name, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return Response.success(
        message="文件上传成功",
        data={
            "original_name": original_filename,
            "disk_name": disk_name,
            "size": file.size,
            "url": f"/uploads/{disk_name}",
        },
    )
