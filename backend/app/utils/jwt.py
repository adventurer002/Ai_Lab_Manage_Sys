import jwt
from app.config import settings
from datetime import datetime, timedelta


# 生成 JWT
def create_access_token(user_id: int) -> str:
    # 过期时间设置
    expire = datetime.now() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    # 生成 payload
    payload = {"usr_id": user_id, "exp": expire}

    # 生成 JWT
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


# 解析JWT
def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
