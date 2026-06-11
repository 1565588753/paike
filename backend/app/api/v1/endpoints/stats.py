from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...models.scheduling import (
    Notification, SpecialDate, TimetableEntry, SwapRequest,
    Teacher, ClassInfo, Subject
)
from ...schemas.common import GenericResponse

router = APIRouter(tags=["统计与通知"])


@router.get("/notifications", response_model=GenericResponse)
def list_notifications(limit: int = 50, db: Session = Depends(get_db),
                       user: User = Depends(get_current_user)):
    items = db.query(Notification).filter(Notification.recipient_user_id == user.id).order_by(
        Notification.created_at.desc()).limit(limit).all()
    for n in items:
        if not n.is_read:
            n.is_read = True
    db.commit()
    return GenericResponse(data=[{"id": n.id, "title": n.title, "content": n.content,
                                  "type": n.type, "is_read": n.is_read,
                                  "created_at": n.created_at.isoformat() if n.created_at else None}
                                 for n in items])


@router.post("/notifications/{nid}/read", response_model=GenericResponse)
def mark_read(nid: int, db: Session = Depends(get_db),
              user: User = Depends(get_current_user)):
    n = db.query(Notification).filter(Notification.id == nid,
                                      Notification.recipient_user_id == user.id).first()
    if n:
        n.is_read = True
        db.commit()
    return GenericResponse(message="已标为已读")


# ---------- Statistics ----------
@router.get("/stats/teacher-workload", response_model=GenericResponse)
def teacher_workload(version_id: int, db: Session = Depends(get_db),
                     user: User = Depends(get_current_user)):
    entries = db.query(TimetableEntry).filter(TimetableEntry.version_id == version_id).all()
    teachers = {t.id: t for t in db.query(Teacher).all()}
    workload = {}
    for e in entries:
        workload[e.teacher_id] = workload.get(e.teacher_id, 0) + 1
    data = [{"teacher_id": tid, "teacher_name": teachers[tid].name, "hours": h}
            for tid, h in workload.items() if tid in teachers]
    data.sort(key=lambda x: -x["hours"])
    return GenericResponse(data=data)


@router.get("/stats/classroom-utilization", response_model=GenericResponse)
def classroom_utilization(version_id: int, db: Session = Depends(get_db),
                          user: User = Depends(get_current_user)):
    from ...models.scheduling import Classroom
    entries = db.query(TimetableEntry).filter(
        TimetableEntry.version_id == version_id,
        TimetableEntry.classroom_id != None
    ).all()
    rooms = {r.id: r for r in db.query(Classroom).all()}
    stats = {}
    for e in entries:
        stats[e.classroom_id] = stats.get(e.classroom_id, 0) + 1
    data = [{"classroom_id": rid, "name": rooms[rid].name, "hours": h}
            for rid, h in stats.items() if rid in rooms]
    return GenericResponse(data=data)


@router.get("/stats/subject-distribution", response_model=GenericResponse)
def subject_distribution(version_id: int, db: Session = Depends(get_db),
                         user: User = Depends(get_current_user)):
    entries = db.query(TimetableEntry).filter(TimetableEntry.version_id == version_id).all()
    subjects = {s.id: s for s in db.query(Subject).all()}
    counts = {}
    for e in entries:
        counts[e.subject_id] = counts.get(e.subject_id, 0) + 1
    data = [{"subject_id": sid, "name": subjects[sid].name, "count": c}
            for sid, c in counts.items() if sid in subjects]
    return GenericResponse(data=data)


# ---------- Special dates ----------
@router.get("/special-dates", response_model=GenericResponse)
def list_special_dates(academic_year_id: int, db: Session = Depends(get_db),
                       user: User = Depends(get_current_user)):
    items = db.query(SpecialDate).filter(SpecialDate.academic_year_id == academic_year_id).all()
    return GenericResponse(data=[{"id": s.id, "date": str(s.date), "type": s.type,
                                  "name": s.name, "remark": s.remark} for s in items])


@router.post("/special-dates", response_model=GenericResponse)
def create_special_date(payload: dict, db: Session = Depends(get_db),
                        user: User = Depends(get_current_user)):
    s = SpecialDate(academic_year_id=payload["academic_year_id"],
                    semester_id=payload.get("semester_id"),
                    date=payload["date"], type=payload["type"],
                    name=payload["name"], remark=payload.get("remark"))
    db.add(s)
    db.commit()
    db.refresh(s)
    return GenericResponse(data={"id": s.id})
