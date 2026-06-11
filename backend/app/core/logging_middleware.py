from datetime import datetime
from fastapi import Request
from sqlalchemy.orm import Session
from ..models.log import OperationLog
from app.core.database import SessionLocal


def log_operation(user_id: int = None, username: str = None, operation: str = None,
                  module: str = None, method: str = None, params: str = None,
                  ip: str = None, status: int = 1, error_msg: str = None):
    try:
        db = SessionLocal()
        log = OperationLog(
            user_id=user_id, username=username, operation=operation,
            module=module, method=method, params=params,
            ip_address=ip, status=status, error_msg=error_msg
        )
        db.add(log)
        db.commit()
        db.close()
    except Exception:
        pass
