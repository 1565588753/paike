import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用
    APP_NAME: str = "智慧教务与智能排课管理平台"
    APP_ENV: str = os.getenv("APP_ENV", "dev")

    # 数据库 - 支持 SQLite / MySQL 通过 DATABASE_URL 直接覆盖
    DB_HOST: str = os.getenv("DB_HOST", "mysql")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "root")
    DB_NAME: str = os.getenv("DB_NAME", "school_scheduling")

    # 如显式提供 DATABASE_URL 则直接使用(可用于sqlite:///... 或其他)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-please-in-production-0x1F2E3D4C5B")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

    # CORS
    CORS_ORIGINS: list = ["*"]

    # 日志
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
