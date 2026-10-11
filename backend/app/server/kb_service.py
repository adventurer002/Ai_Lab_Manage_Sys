import asyncio
import os

# 国内直连 huggingface.co 会被网络重置，模型加载时的版本校验会挂起。
# 改用国内镜像，模型加载/更新均无需开启代理（必须在 import chromadb 之前设置）
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

from chromadb.api.models.Collection import Collection

from chromadb.utils import embedding_functions
import chromadb
from app.config import BASE_DIR

KB_DIR = BASE_DIR / "data" / "kb"
CHROMA_DIR = BASE_DIR / "data" / "chroma"

_collection = None
_embedding_fn = None
_init_lock = asyncio.Lock()


async def get_embedding_fn():
    """懒加载 embedding 模型：只加载一次，之后复用同一个实例"""
    global _embedding_fn
    if _embedding_fn is None:
        # 模型首次加载是磁盘/网络阻塞操作，丢到线程池避免卡住事件循环
        _embedding_fn = await asyncio.to_thread(
            embedding_functions.SentenceTransformerEmbeddingFunction,
            model_name="BAAI/bge-small-zh-v1.5",
        )
    return _embedding_fn


async def get_collection() -> Collection:
    """向量库的初始化（异步）"""

    global _collection
    # 如果向量库已存在，直接返回向量库
    if _collection is not None:
        return _collection

    # 加锁 + 二次判断，避免并发首请求时重复加载模型、重复灌库
    async with _init_lock:
        if _collection is not None:
            return _collection

        KB_DIR.mkdir(parents=True, exist_ok=True)  # 确保目录存在
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)  # 确保目录存在

        # 懒加载中文 embedding 模型
        embedding_fn = await get_embedding_fn()
        # 创建一个 Chroma 客户端，数据是 持久化 存到磁盘的
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        # 获取或创建向量库
        col = await asyncio.to_thread(
            client.get_or_create_collection,
            name="lab_kb",
            embedding_function=embedding_fn,
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


async def warmup():
    """启动时预热：把模型加载 + 首次检索的开销付在启动阶段，别落在第一个用户请求上"""
    col = await get_collection()
    if await asyncio.to_thread(col.count) > 0:
        await asyncio.to_thread(col.query, query_texts=["预热"], n_results=1)


async def search(query: str):
    """根据关键字去检索向量库（异步）"""
    col = await get_collection()
    count = await asyncio.to_thread(col.count)
    if count == 0:
        return ""
    # 最多查 5 条，但如果库里不足 5 条，就查实际数量。`min` 防止`n_results` 超过实际数量报错。
    limit = min(5, count)
    res = await asyncio.to_thread(col.query, query_texts=[query], n_results=limit)
    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    distances = (res.get("distances") or [[]])[0]

    # 以下是检索出来的资料格式示例：
    # [预约规则.md]
    # # 实验室预约规则...
    # [安全规范.md]
    # 安全规范....
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
