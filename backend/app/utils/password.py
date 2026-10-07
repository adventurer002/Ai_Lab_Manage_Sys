import bcrypt


# 秘密加密
def hash_password(password: str) -> str:
    # 返回加密密码
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# 秘密验证
def verify_password(password: str, hashed_password: str) -> bool:
    # 验证密码是否匹配
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
