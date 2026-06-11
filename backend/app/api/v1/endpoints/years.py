from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user, RoleRequired
from app.models.user import User
from app.models.scheduling import AcademicYear, Semester
from app.schemas.common import GenericResponse

router = APIRouter(tags=["学年学期"])


@router.get("", response_model=GenericResponse)
def list_years(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.query(AcademicYear).order_by(AcademicYear.name.desc()).all()
    return GenericResponse(data=[{"id": y.id, "name": y.name, "start_date": str(y.start_date),
                                  "end_date": str(y.end_date), "is_archived": y.is_archived,
                                  "is_current": y.is_current} for y in items])


@router.post("", response_model=GenericResponse)
def create_year(payload: dict, db: Session = Depends(get_db),
                user: User = Depends(RoleRequired(["admin", "academic"]))):
    if db.query(AcademicYear).filter(AcademicYear.name == payload.get("name")).first():
        raise HTTPException(status_code=400, detail="学年名称已存在")
    y = AcademicYear(name=payload["name"], start_date=payload["start_date"],
                     end_date=payload["end_date"], is_current=payload.get("is_current", False))
    db.add(y)
    db.commit()
    db.refresh(y)
    return GenericResponse(data={"id": y.id})


@router.put("/{year_id}/set-current", response_model=GenericResponse)
def set_current(year_id: int, db: Session = Depends(get_db),
                user: User = Depends(RoleRequired(["admin", "academic"]))):
    db.query(AcademicYear).update({AcademicYear.is_current: False})
    y = db.query(AcademicYear).filter(AcademicYear.id == year_id).first()
    if y:
        y.is_current = True
    db.commit()
    return GenericResponse(message="设为当前学年")


@router.post("/{year_id}/archive", response_model=GenericResponse)
def archive_year(year_id: int, db: Session = Depends(get_db),
                 user: User = Depends(RoleRequired(["admin", "academic"]))):
    y = db.query(AcademicYear).filter(AcademicYear.id == year_id).first()
    if y:
        y.is_archived = True
        db.commit()
    return GenericResponse(message="已归档")


@router.get("/{year_id}/semesters", response_model=GenericResponse)
def list_semesters(year_id: int, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    items = db.query(Semester).filter(Semester.academic_year_id == year_id).all()
    return GenericResponse(data=[{"id": s.id, "name": s.name, "start_date": str(s.start_date),
                                  "end_date": str(s.end_date), "total_weeks": s.total_weeks,
                                  "is_current": s.is_current}
                                 for s in items])


@router.post("/{year_id}/semesters", response_model=GenericResponse)
def create_semester(year_id: int, payload: dict, db: Session = Depends(get_db),
                    user: User = Depends(RoleRequired(["admin", "academic"]))):
    s = Semester(academic_year_id=year_id, name=payload["name"],
                 start_date=payload["start_date"], end_date=payload["end_date"],
                 total_weeks=payload.get("total_weeks", 20),
                 is_current=payload.get("is_current", False))
    db.add(s)
    db.commit()
    db.refresh(s)
    return GenericResponse(data={"id": s.id})


@router.post("/semesters/{semester_id}/set-current", response_model=GenericResponse)
def set_current_semester(semester_id: int, db: Session = Depends(get_db),
                         user: User = Depends(RoleRequired(["admin", "academic"]))):
    s = db.query(Semester).filter(Semester.id == semester_id).first()
    if not s:
        raise HTTPException(status_code=404)
    db.query(Semester).update({Semester.is_current: False})
    s.is_current = True
    db.commit()
    return GenericResponse(message="设为当前学期")


# ---------- 学年升级 ----------
@router.post("/{year_id}/upgrade", response_model=GenericResponse)
def upgrade_year(year_id: int, target_year_id: int, db: Session = Depends(get_db),
                 user: User = Depends(RoleRequired(["admin", "academic"]))):
    """将现有班级升到下一年级，并创建新一年级。"""
    from app.models.scheduling import ClassInfo, Grade
    grades = {g.level: g.id for g in db.query(Grade).all()}
    classes = db.query(ClassInfo).filter(ClassInfo.academic_year_id == year_id).all()
    new_classes = []
    for c in classes:
        current_level = next((k for k, v in grades.items() if v == c.grade_id), None)
        if current_level is None:
            continue
        if current_level >= 6:
            continue  # 六年级毕业，不升入
        new_level = current_level + 1
        new_class = ClassInfo(
            name=f"{new_level}({c.name.split('(')[-1].rstrip('班') or '1'})班",
            grade_id=grades[new_level],
            student_count=c.student_count,
            schedule_plan_id=c.schedule_plan_id,
            academic_year_id=target_year_id,
            status=1
        )
        db.add(new_class)
        new_classes.append(new_class)
    # 创建新一年级
    new_grade_id = grades.get(1)
    if new_grade_id:
        for i in range(1, 3):
            nc = ClassInfo(name=f"一({i})班", grade_id=new_grade_id, student_count=40,
                           academic_year_id=target_year_id, status=1)
            db.add(nc)
    db.commit()
    return GenericResponse(message=f"升级完成, 升班{len(new_classes)}个")
