import traceback

from openai import AsyncOpenAI

import json

from app.schemas.ai import ChatMessage, ChatRequest
from app.config import settings
from app.common.exceptions import BusinessException
from app.server.kb_service import search
from sqlalchemy.ext.asyncio import AsyncSession
from app.server import equipment_service, lab_service

SYSTEM_PROMPT = """你是智能实验室预约系统的助手，回答要简洁。
如果下面提供了实验室资料，请依据资料回答规则、安全、文档里的开放时间说明。
查询当前有哪些开放实验室、某实验室有哪些设备时，必须调用工具，不要编造。
你不能替用户提交预约，也不能直接改数据库。
如果用户要预约，请说明去「实验室列表」选择后提交，等待管理员审核。
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_open_labs",
            "description": "查询当前开放中的实验室列表，可以按名称关键字来筛选",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "string",
                        "description": "实验室的名称关键字，可以为空",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_lab_equipments",
            "description": "查询某个实验室下的设备列表。如果用户只提供了实验室名称而没有 lab_id，必须先调用 list_open_labs 查询到 lab_id，再调用本工具",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab_id": {
                        "type": "integer",
                        "description": "实验室 ID",
                    },
                    "keywords": {
                        "type": "string",
                        "description": "设备名称的关键字，可以为空",
                    },
                },
            },
        },
    },
]


# 调用工具方法
async def run_tool(db: AsyncSession, name: str, arguments: str) -> str:
    try:
        args = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return json.dumps({"error": "参数不是合法的json"}, ensure_ascii=False)

    try:
        if name == "list_open_labs":
            keywords = (args.get("keywords") or "").strip() or None
            page = await lab_service.get_lab_list_service(
                db, page=1, page_size=20, keyword=keywords, status=1
            )
            rows = [
                {
                    "id": item.id,
                    "name": item.name,
                    "location": item.location,
                    "capacity": item.capacity,
                    "open_time": item.open_time,
                    "close_time": item.close_time,
                }
                for item in page.items
            ]
            return json.dumps(
                {"total": page.total, "labs": rows}, ensure_ascii=False, default=str
            )

        if name == "list_lab_equipments":
            lab_id = args.get("lab_id")
            if not lab_id:
                return json.dumps(
                    {"error": "参数缺少实验室 lab_id"}, ensure_ascii=False
                )
            keywords = (args.get("keywords") or "").strip() or None
            page = await equipment_service.get_equipment_list_service(
                db, page=1, page_size=50, lab_id=int(lab_id), keyword=keywords
            )
            rows = [
                {
                    "id": item.id,
                    "name": item.name,
                    "lab_id": item.lab_id,
                    "lab_name": item.lab_name,
                    "spec": item.spec,
                    "quantity": item.quantity,
                    "status": "正常" if item.status == 1 else "维修中",
                }
                for item in page.items
            ]
            return json.dumps(
                {"total": page.total, "equipments": rows}, ensure_ascii=False
            )

        return json.dumps({"error": f"未找到工具：{name}"}, ensure_ascii=False)

    except Exception as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)


# 获取OpenAI客户端
async def get_client():
    """获取OpenAI客户端"""
    if not settings.LLM_API_KEY:
        raise BusinessException(message="请配置OpenAI API密钥")
    client = AsyncOpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
    )
    return client


# 大模型对话逻辑
async def chat_service(data: ChatRequest, db: AsyncSession):
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
    messages = [
        {"role": "system", "content": system_prompt},
        *history,
    ]

    try:
        for _ in range(5):
            res = await client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
            Msg = res.choices[0].message
            tool_calls = Msg.tool_calls or []

            if not tool_calls:
                content = Msg.content
                if not content or not content.strip():
                    raise BusinessException(message="大模型没有返回内容")
                return content

            messages.append(
                {
                    "role": "assistant",
                    "content": Msg.content or "",
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.function.name,
                                "arguments": call.function.arguments,
                            },
                        }
                        for call in tool_calls
                    ],
                }
            )
            for call in tool_calls:
                result = await run_tool(db, call.function.name, call.function.arguments)
                messages.append(
                    {"role": "tool", "content": result, "tool_call_id": call.id}
                )
        raise BusinessException(message="工具调用次数过多，请稍后重试")
    except BusinessException:
        raise
    except Exception:
        traceback.print_exc()
        raise BusinessException(message="大模型调用失败，请稍后重试")
