import asyncio

from chromadb.api.models.Collection import Collection

from chromadb.utils import embedding_functions
import chromadb
from app.config import BASE_DIR

KB_DIR = BASE_DIR / "data" / "kb"
CHROMA_DIR = BASE_DIR / "data" / "chroma"

_collection = None

_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-zh-v1.5"
)


async def get_collection() -> Collection:
    """向量库的初始化（异步）"""

    global _collection
    # 如果向量库已存在，直接返回向量库
    if _collection is not None:
        return _collection

    KB_DIR.mkdir(parents=True, exist_ok=True)  # 确保目录存在
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)  # 确保目录存在

    # 创建一个 Chroma 客户端，数据是 持久化 存到磁盘的
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    # 获取或创建向量库
    col = await asyncio.to_thread(
        client.get_or_create_collection,
        name="lab_kb",
        embedding_function=_embedding_fn,
    )
    # 如果向量库为空，添加所有文档
    if await asyncio.to_thread(col.count) == 0:
        ids = []
        docs = []
        metas = []
        for path in sorted(KB_DIR.glob("*.md")):
            text = path.read_text(encoding="UTF-8").strip()
            if not text:
                continue
            docs.append(text)
            ids.append(path.stem)
            metas.append({"source": path.name})
        if docs:
            await asyncio.to_thread(
                col.add, ids=ids, documents=docs, metadatas=metas
            )
    _collection = col
    return col


async def search(query: str):
    """根据关键字去检索向量库（异步）"""
    col = await get_collection()
    count = await asyncio.to_thread(col.count)
    if count == 0:
        return ""
    # 最多查 5 条，但如果库里不足 5 条，就查实际数量。`min` 防止`n_results` 超过实际数量报错。
    limit = min(5, count)
    res = await asyncio.to_thread(
        col.query, query_texts=[query], n_results=limit
    )
    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    distances = (res.get("distances") or [[]])[0]

    """
    以下是检索出来的资料：
    [预约规则.md]

    # 实验室预约规则...

    
    [安全规范.md]

    安全规范....
    """
    score_parts = []
    for doc, metas, dist in zip(docs, metas, distances):
        # 0-1 越接近1表示越相关
        score = 1 / (1 + dist)
        if score < 0.5:
            continue
        name = metas.get("source") or ""
        score_parts.append({"score": score, "content": f"[{name}]\n{doc}"})
    print(f"检索出来的 score_parts：{score_parts}")
    score_parts.sort(key=lambda x: x["score"], reverse=True)
    final_parts = [item["content"] for item in score_parts[:2]]
    return "\n\n".join(final_parts)
