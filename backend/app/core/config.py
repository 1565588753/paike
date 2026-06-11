from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 应用
    APP_NAME: str = "智慧教务与智能排课管理平台"
    APP_ENV: str = "dev"

    # 数据库
    DB_HOST: str = "mysql"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "root"
    DB_NAME: str = "school_scheduling"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # JWT
    JWT_SECRET: str = "change-me-please-in-production-0x1F2E3D4C5B"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # 日志
    LOG_LEVEL: str = "info"

    class Config:
        env_file = ".env"


settings = Settings()
