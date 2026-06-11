from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user, RoleRequired, hash_password
from app.models.user import User
from app.models.scheduling import Teacher
from app.schemas.common import TeacherCreate, TeacherResponse, GenericResponse
from app.services.repositories import TeacherRepository

router = APIRouter(prefix="/teachers", tags=["教师"])


@router.get("", response_model=GenericResponse)
def list_teachers(
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    user: User = Depends(RoleRequired(["admin", "academic"]))):
    repo = TeacherRepository(db)
    items = repo.list(keyword=keyword, skip=(page - 1) * page_size, limit=page_size)
    total = repo.count(keyword=keyword)
    return GenericResponse(data={"items": [
        {"id": t.id, "teacher_no": t.teacher_no, "name": t.name, "gender": t.gender,
         "phone": t.phone, "title": t.title, "main_subject_id": t.main_subject_id,
         "subject_ids": t.subject_ids, "max_weekly_hours": t.max_weekly_hours,
         "max_daily_hours": t.max_daily_hours, "status": t.status,
         "created_at": t.created_at.isoformat() if t.created_at else None}
        for t in items
    ], "total": total, "page": page, "page_size": page_size})


@router.post("", response_model=GenericResponse)
def create_teacher(payload: TeacherCreate, db: Session = Depends(get_db),
                   user: User = Depends(RoleRequired(["admin", "academic"]))):
    repo = TeacherRepository(db)
    if repo.get_by_no(payload.teacher_no):
        raise HTTPException(status_code=400, detail="工号已存在")
    t = Teacher(**payload.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    # 自动创建账号
    existing = db.query(User).filter(User.username == payload.teacher_no).first()
    if not existing:
        u = User(username=payload.teacher_no, password_hash=hash_password("123456"),
                 real_name=payload.name, role_code="teacher", teacher_id=t.id, first_login=True)
        db.add(u)
        db.commit()
    return GenericResponse(data={"id": t.id}, message="创建成功")


@router.put("/{teacher_id}", response_model=GenericResponse)
def update_teacher(teacher_id: int, payload: TeacherCreate, db: Session = Depends(get_db),
                   user: User = Depends(RoleRequired(["admin", "academic"]))):
    t = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="教师不存在")
    for k, v in payload.model_dump().items():
        setattr(t, k, v)
    db.commit()
    return GenericResponse(message="更新成功")


@router.delete("/{teacher_id}", response_model=GenericResponse)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db),
                   user: User = Depends(RoleRequired(["admin", "academic"]))):
    t = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="教师不存在")
    t.status = 0
    db.commit()
    return GenericResponse(message="已停用")


@router.get("/all", response_model=GenericResponse)
def all_teachers(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.query(Teacher).filter(Teacher.status == 1).order_by(Teacher.name).all()
    return GenericResponse(data=[{"id": t.id, "name": t.name, "teacher_no": t.teacher_no,
                                  "main_subject_id": t.main_subject_id, "subject_ids": t.subject_ids}
                                 for t in items])
