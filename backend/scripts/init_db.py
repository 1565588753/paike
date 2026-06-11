import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from sqlalchemy import create_engine, text
from app.core.config import settings

DB_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"


def wait_for_db(max_retries=30):
    for i in range(max_retries):
        try:
            engine = create_engine(DB_URL)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("数据库连接成功")
            return engine
        except Exception as e:
            print(f"等待数据库连接... ({i+1}/{max_retries}) {e}")
            time.sleep(3)
    raise Exception("数据库连接超时")


def run_sql_file(engine, filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        sql_content = f.read()
    # 按分号拆分语句, 忽略空语句
    statements = [s.strip() for s in sql_content.split(";") if s.strip() and not s.strip().startswith("--")]
    with engine.connect() as conn:
        for stmt in statements:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception as e:
                # 忽略一些重复插入等警告错误
                if "Duplicate" not in str(e) and "already exists" not in str(e).lower():
                    print(f"  [WARN] {str(e)[:100]}")
                conn.rollback()


if __name__ == "__main__":
    engine = wait_for_db()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sql_dir = os.path.join(base_dir, "sql")
    print("执行 01_schema.sql ...")
    run_sql_file(engine, os.path.join(sql_dir, "01_schema.sql"))
    print("执行 02_init_data.sql ...")
    run_sql_file(engine, os.path.join(sql_dir, "02_init_data.sql"))
    print("数据库初始化完成")
