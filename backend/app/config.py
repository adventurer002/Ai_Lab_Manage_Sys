from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# 项目根目录（config.py 的上上级）
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_EXPIRE_HOURS: int
    JWT_ALGORITHM: str
    LLM_API_KEY: str
    LLM_BASE_URL: str
    LLM_MODEL: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # 可选：忽略 .env 里多余的变量
    )


MAX_FILE_SIZE = 100 * 1024 * 1024
FILE_PATH = BASE_DIR / "uploads"
FILE_PATH.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".zip",
}


settings = Settings()
