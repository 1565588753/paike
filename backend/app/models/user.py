from sqlalchemy import Column, BigInteger, String, DateTime, SmallInteger, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "sys_user"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(64), nullable=False)
    avatar = Column(String(255))
    phone = Column(String(32))
    email = Column(String(128))
    role_code = Column(String(32), nullable=False, default="teacher")
    teacher_id = Column(BigInteger)
    first_login = Column(Boolean, default=True)
    status = Column(SmallInteger, default=1)
    last_login_at = Column(DateTime)
    created_by = Column(BigInteger)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Role(Base):
    __tablename__ = "sys_role"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_code = Column(String(32), unique=True, nullable=False)
    role_name = Column(String(64), nullable=False)
    description = Column(String(255))
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=func.now())


class Permission(Base):
    __tablename__ = "sys_permission"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    perm_code = Column(String(128), unique=True, nullable=False)
    perm_name = Column(String(128), nullable=False)
    module = Column(String(64))
    created_at = Column(DateTime, default=func.now())


class RolePermission(Base):
    __tablename__ = "sys_role_permission"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_code = Column(String(32), nullable=False)
    perm_code = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=func.now())
