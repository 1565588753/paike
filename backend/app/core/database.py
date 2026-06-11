import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings


def get_db_url():
    # 1) 优先 DATABASE_URL 环境变量
    if settings.DATABASE_URL:
        return settings.DATABASE_URL
    # 2) 本地调试无 MySQL 时自动 fallback 到 SQLite
    db_host = settings.DB_HOST or ""
    if not db_host or db_host.lower() in ("sqlite", "", "none") or os.getenv("USE_SQLITE", "0") == "1":
        path = os.path.join(os.path.dirname(__file__), "..", "school_scheduling.sqlite3")
        return f"sqlite:///{path}"
    # 3) MySQL
    return f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"


DATABASE_URL = get_db_url()

engine_kwargs = {
    "pool_pre_ping": True,
    "echo": settings.LOG_LEVEL == "debug",
}
if "sqlite" in DATABASE_URL:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({"pool_size": 20, "max_overflow": 30, "pool_recycle": 3600})

engine = create_engine(DATABASE_URL, **engine_kwargs)

# SQLite 开启外键
if "sqlite" in DATABASE_URL:
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        except Exception:
            pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
