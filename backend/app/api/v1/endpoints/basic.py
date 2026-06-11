from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user, RoleRequired
from app.models.user import User
from app.models.scheduling import ClassInfo, Grade, Classroom, Subject
from app.schemas.common import ClassInfoBase, ClassroomBase, SubjectBase, GenericResponse

router = APIRouter(tags=["基础数据"])


# ---------- ClassInfo ----------
@router.get("/classes", response_model=GenericResponse)
def list_classes(academic_year_id: Optional[int] = None, grade_id: Optional[int] = None,
                 db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(ClassInfo)
    if academic_year_id:
        q = q.filter(ClassInfo.academic_year_id == academic_year_id)
    if grade_id:
        q = q.filter(ClassInfo.grade_id == grade_id)
    items = q.order_by(ClassInfo.name).all()
    return GenericResponse(data=[{"id": c.id, "name": c.name, "grade_id": c.grade_id,
                                  "student_count": c.student_count, "schedule_plan_id": c.schedule_plan_id,
                                  "academic_year_id": c.academic_year_id}
                                 for c in items])


@router.post("/classes", response_model=GenericResponse)
def create_class(payload: ClassInfoBase, db: Session = Depends(get_db),
                 user: User = Depends(RoleRequired(["admin", "academic"]))):
    c = ClassInfo(**payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return GenericResponse(data={"id": c.id})


@router.put("/classes/{class_id}", response_model=GenericResponse)
def update_class(class_id: int, payload: ClassInfoBase, db: Session = Depends(get_db),
                 user: User = Depends(RoleRequired(["admin", "academic"]))):
    c = db.query(ClassInfo).filter(ClassInfo.id == class_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="不存在")
    for k, v in payload.model_dump().items():
        setattr(c, k, v)
    db.commit()
    return GenericResponse(message="更新成功")


@router.delete("/classes/{class_id}", response_model=GenericResponse)
def delete_class(class_id: int, db: Session = Depends(get_db),
                 user: User = Depends(RoleRequired(["admin", "academic"]))):
    c = db.query(ClassInfo).filter(ClassInfo.id == class_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="不存在")
    db.delete(c)
    db.commit()
    return GenericResponse(message="删除成功")


# ---------- Grades ----------
@router.get("/grades", response_model=GenericResponse)
def list_grades(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.query(Grade).order_by(Grade.level).all()
    return GenericResponse(data=[{"id": g.id, "name": g.name, "level": g.level} for g in items])


# ---------- Subjects ----------
@router.get("/subjects", response_model=GenericResponse)
def list_subjects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.query(Subject).filter(Subject.status == 1).order_by(Subject.sort_order).all()
    return GenericResponse(data=[{"id": s.id, "name": s.name, "code": s.code, "is_main": s.is_main,
                                  "need_room": s.need_room, "color": s.color, "sort_order": s.sort_order}
                                 for s in items])


@router.post("/subjects", response_model=GenericResponse)
def create_subject(payload: SubjectBase, db: Session = Depends(get_db),
                   user: User = Depends(RoleRequired(["admin", "academic"]))):
    s = Subject(**payload.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return GenericResponse(data={"id": s.id})


# ---------- Classroom ----------
@router.get("/classrooms", response_model=GenericResponse)
def list_classrooms(type: Optional[str] = None, db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    q = db.query(Classroom).filter(Classroom.status == 1)
    if type:
        q = q.filter(Classroom.type == type)
    items = q.order_by(Classroom.name).all()
    return GenericResponse(data=[{"id": r.id, "name": r.name, "type": r.type, "capacity": r.capacity,
                                  "location": r.location, "subject_ids": r.subject_ids}
                                 for r in items])


@router.post("/classrooms", response_model=GenericResponse)
def create_classroom(payload: ClassroomBase, db: Session = Depends(get_db),
                     user: User = Depends(RoleRequired(["admin", "academic"]))):
    r = Classroom(**payload.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return GenericResponse(data={"id": r.id})


@router.put("/classrooms/{room_id}", response_model=GenericResponse)
def update_classroom(room_id: int, payload: ClassroomBase, db: Session = Depends(get_db),
                     user: User = Depends(RoleRequired(["admin", "academic"]))):
    r = db.query(Classroom).filter(Classroom.id == room_id).first()
    if not r:
        raise HTTPException(status_code=404)
    for k, v in payload.model_dump().items():
        setattr(r, k, v)
    db.commit()
    return GenericResponse(message="更新成功")
