from openai import AsyncOpenAI
from app.schemas.ai import ChatMessage, ChatRequest
from app.config import settings
from app.common.exceptions import BusinessException
from app.server.kb_service import search


SYSTEM_PROMPT = """你是智能实验室预约系统的助手，回答要简洁。
如果下面提供了实验室资料，请依据资料回答，不要编造资料里没有的时间、规则、设备。
你目前查不到真实的实验室空闲、设备库存、预约记录。
如果用户问现在哪些实验室能约、某台设备此刻有没有空，请说明去「实验室列表」查看。
除了实验室相关的问题之外，不要回复无关的问题。
"""


async def get_client():
    """获取OpenAI客户端"""
    if not settings.LLM_API_KEY:
        raise BusinessException(message="请配置OpenAI API密钥")
    client = AsyncOpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
    )
    return client


async def chat_service(data: ChatRequest):
    """大模型对话"""
    if not data.messages:
        raise BusinessException(message="对话内容为空")
    history = []
    for message in data.messages:
        if message.role in ("user", "assistant") and message.content.strip():
            history.append(message.model_dump())
    if not history:
        raise BusinessException(message="请输入您要对话的内容")

    # 取出用户最新的一条提问内容
    question = next(
        (item["content"] for item in reversed(history) if item["role"] == "user"), ""
    )
    knowledge = await search(query=question)
    print(f"检索到的向量库的内容：{knowledge}")
    system_prompt = SYSTEM_PROMPT
    if knowledge:
        system_prompt += "\n\n以下是检索到的实验室的资料：\n" + knowledge

    client = await get_client()
    try:
        res = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                ChatMessage(role="system", content=system_prompt).model_dump(),
                *history,
            ],
        )
        content = res.choices[0].message.content
        if not content.strip():
            raise BusinessException(message="大模型没有返回内容")
        return content
    except BusinessException:
        raise
    except Exception:
        raise BusinessException(message="大模型调用失败，请稍后重试")
