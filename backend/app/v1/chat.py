from fastapi import APIRouter

from app.schemas.ai import ChatMessage
from app.schemas.ai import ChatRequest
from app.server.ai_service import chat_service
from app.common.exceptions import BusinessException
from app.common.response import Response


router = APIRouter(prefix="/ai")


@router.post("/chat")
async def chat(data: ChatRequest):
    """调用模型"""
    content = await chat_service(data)
    return Response.success(data=ChatMessage(role="assistant", content=content))
