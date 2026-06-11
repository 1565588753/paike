from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import json
from app.core.database import get_db
from app.core.security import get_current_user, RoleRequired
from app.models.user import User
from app.models.scheduling import HRRecord, SchedulePlan, TimeSlot, CourseCycle, SubjectWeeklyPlan
from app.schemas.common import GenericResponse

router = APIRouter(tags=["人事表与作息"])


@router.get("/schedule-plans", response_model=GenericResponse)
def list_schedule_plans(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plans = db.query(SchedulePlan).all()
    result = []
    for p in plans:
        slots = db.query(TimeSlot).filter(TimeSlot.schedule_plan_id == p.id).order_by(TimeSlot.sort_order).all()
        result.append({"id": p.id, "name": p.name, "description": p.description,
                       "is_default": p.is_default,
                       "slots": [{"id": s.id, "period_no": s.period_no, "period_name": s.period_name,
                                  "start_time": s.start_time, "end_time": s.end_time,
                                  "is_break": s.is_break, "sort_order": s.sort_order} for s in slots]})
    return GenericResponse(data=result)


@router.post("/schedule-plans", response_model=GenericResponse)
def create_schedule_plan(payload: dict, db: Session = Depends(get_db),
                         user: User = Depends(RoleRequired(["admin", "academic"]))):
    p = SchedulePlan(name=payload["name"], description=payload.get("description"), is_default=payload.get("is_default", False))
    db.add(p)
    db.commit()
    db.refresh(p)
    for s in payload.get("slots", []):
        slot = TimeSlot(schedule_plan_id=p.id, period_no=s.get("period_no", 0),
                        period_name=s["period_name"], start_time=s["start_time"],
                        end_time=s["end_time"], is_break=s.get("is_break", False),
                        sort_order=s.get("sort_order", 0))
        db.add(slot)
    db.commit()
    return GenericResponse(data={"id": p.id})


@router.get("/cycles", response_model=GenericResponse)
def list_cycles(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.query(CourseCycle).all()
    return GenericResponse(data=[{"id": c.id, "code": c.code, "name": c.name,
                                  "week_mask": c.week_mask} for c in items])


# ---------- HR records ----------
@router.get("/hr-records", response_model=GenericResponse)
def list_hr(academic_year_id: int, semester_id: int, db: Session = Depends(get_db),
            user: User = Depends(get_current_user)):
    records = db.query(HRRecord).filter(
        HRRecord.academic_year_id == academic_year_id,
        HRRecord.semester_id == semester_id
    ).all()
    return GenericResponse(data=[{"id": r.id, "class_id": r.class_id,
                                  "head_teacher_id": r.head_teacher_id,
                                  "subject_teachers": r.subject_teachers, "remark": r.remark}
                                 for r in records])


@router.post("/hr-records", response_model=GenericResponse)
def upsert_hr(payload: dict, db: Session = Depends(get_db),
              user: User = Depends(RoleRequired(["admin", "academic"]))):
    r = db.query(HRRecord).filter(
        HRRecord.class_id == payload["class_id"],
        HRRecord.academic_year_id == payload["academic_year_id"],
        HRRecord.semester_id == payload["semester_id"]
    ).first()
    data = {
        "academic_year_id": payload["academic_year_id"],
        "semester_id": payload["semester_id"],
        "class_id": payload["class_id"],
        "head_teacher_id": payload.get("head_teacher_id"),
        "subject_teachers": payload.get("subject_teachers") or {},
        "remark": payload.get("remark")
    }
    if r:
        for k, v in data.items():
            setattr(r, k, v)
    else:
        r = HRRecord(**data)
        db.add(r)
    db.commit()
    db.refresh(r)
    return GenericResponse(data={"id": r.id})


# ---------- Weekly hours ----------
@router.get("/weekly-hours", response_model=GenericResponse)
def list_weekly_hours(academic_year_id: int, semester_id: int,
                      db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.query(SubjectWeeklyPlan).filter(
        SubjectWeeklyPlan.academic_year_id == academic_year_id,
        SubjectWeeklyPlan.semester_id == semester_id
    ).all()
    return GenericResponse(data=[{"id": it.id, "class_id": it.class_id,
                                  "subject_id": it.subject_id, "weekly_hours": it.weekly_hours}
                                 for it in items])


@router.post("/weekly-hours", response_model=GenericResponse)
def upsert_weekly_hours(payload: dict, db: Session = Depends(get_db),
                        user: User = Depends(RoleRequired(["admin", "academic"]))):
    it = db.query(SubjectWeeklyPlan).filter(
        SubjectWeeklyPlan.class_id == payload["class_id"],
        SubjectWeeklyPlan.subject_id == payload["subject_id"],
        SubjectWeeklyPlan.semester_id == payload["semester_id"]
    ).first()
    data = {"academic_year_id": payload["academic_year_id"],
            "semester_id": payload["semester_id"],
            "class_id": payload["class_id"],
            "subject_id": payload["subject_id"],
            "weekly_hours": payload["weekly_hours"]}
    if it:
        for k, v in data.items():
            setattr(it, k, v)
    else:
        it = SubjectWeeklyPlan(**data)
        db.add(it)
    db.commit()
    return GenericResponse(message="保存成功")
