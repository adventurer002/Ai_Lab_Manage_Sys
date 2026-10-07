from fastapi import APIRouter
from .auth import router as auth_router
from .user import router as user_router
from .file import router as file_router
from .lab import router as lab_router
from .equipment import router as equipment_router


v1 = APIRouter(prefix="/v1")
v1.include_router(auth_router)
v1.include_router(user_router)
v1.include_router(file_router)
v1.include_router(lab_router)
v1.include_router(equipment_router)
