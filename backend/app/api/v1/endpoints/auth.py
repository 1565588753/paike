from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.core.security import (
    verify_password, create_access_token, hash_password,
    get_current_user
)
from app.models.user import User
from app.schemas.common import LoginRequest, LoginResponse, PasswordChangeRequest, UserInfoResponse, GenericResponse

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=GenericResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")
    if not user.status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用")

    user.last_login_at = datetime.utcnow()
    db.commit()

    token = create_access_token(subject=user.id, extra={"role": user.role_code})
    return GenericResponse(data={
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "role_code": user.role_code,
        "first_login": user.first_login,
        "teacher_id": user.teacher_id
    })


@router.post("/change-password", response_model=GenericResponse)
def change_password(payload: PasswordChangeRequest, user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if not verify_password(payload.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    user.password_hash = hash_password(payload.new_password)
    user.first_login = False
    db.commit()
    return GenericResponse(message="密码修改成功")


@router.get("/me", response_model=GenericResponse)
def get_me(user: User = Depends(get_current_user)):
    return GenericResponse(data={
        "id": user.id, "username": user.username, "real_name": user.real_name,
        "role_code": user.role_code, "teacher_id": user.teacher_id, "avatar": user.avatar
    })
