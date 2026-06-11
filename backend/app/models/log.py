from sqlalchemy import Column, BigInteger, String, SmallInteger, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class OperationLog(Base):
    __tablename__ = "sys_operation_log"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    username = Column(String(64))
    operation = Column(String(128), nullable=False)
    module = Column(String(64))
    method = Column(String(16))
    params = Column(Text)
    ip_address = Column(String(64))
    status = Column(SmallInteger, default=1)
    error_msg = Column(Text)
    created_at = Column(DateTime, default=func.now())
