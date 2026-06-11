from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from typing import Optional, List
from io import BytesIO
from ...core.database import get_db
from ...core.security import get_current_user, RoleRequired
from ...models.user import User
from ...models.scheduling import (
    TimetableVersion, TimetableEntry, TimetableQuality,
    ClassInfo, Subject, Teacher, Classroom, TimeSlot, AdjustmentRecord
)
from ...services.scheduling_engine import SchedulingEngine
from ...services.conflict_detector import ConflictDetector
from ...services.quality_evaluator import QualityEvaluator
from ...services.export_service import ExportService
from ...schemas.common import TimetableMoveRequest, TimetableSwapRequest, GenericResponse

router = APIRouter(tags=["课表管理"])


@router.get("/versions", response_model=GenericResponse)
def list_versions(academic_year_id: int, semester_id: int,
                  db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    versions = db.query(TimetableVersion).filter(
        TimetableVersion.academic_year_id == academic_year_id,
        TimetableVersion.semester_id == semester_id
    ).order_by(TimetableVersion.created_at.desc()).all()
    return GenericResponse(data=[{"id": v.id, "version_no": v.version_no,
                                  "version_name": v.version_name, "status": v.status,
                                  "created_at": v.created_at.isoformat() if v.created_at else None,
                                  "quality_score": v.quality_score, "published_at": v.published_at.isoformat() if v.published_at else None}
                                 for v in versions])


@router.post("/versions", response_model=GenericResponse)
def create_version(academic_year_id: int, semester_id: int,
                   version_name: Optional[str] = None,
                   db: Session = Depends(get_db),
                   user: User = Depends(RoleRequired(["admin", "academic"]))):
    max_v = db.query(TimetableVersion).filter(
        TimetableVersion.academic_year_id == academic_year_id,
        TimetableVersion.semester_id == semester_id
    ).count()
    v = TimetableVersion(
        academic_year_id=academic_year_id,
        semester_id=semester_id,
        version_no=f"V{max_v + 1:03d}",
        version_name=version_name or f"V{max_v + 1:03d}",
        status="draft", created_by=user.id
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return GenericResponse(data={"id": v.id, "version_no": v.version_no})


@router.post("/versions/{version_id}/publish", response_model=GenericResponse)
def publish_version(version_id: int, db: Session = Depends(get_db),
                    user: User = Depends(RoleRequired(["admin", "academic"]))):
    from datetime import datetime
    db.query(TimetableVersion).filter(
        TimetableVersion.id != version_id,
        TimetableVersion.status == "published"
    ).update({TimetableVersion.status: "draft"})
    v = db.query(TimetableVersion).filter(TimetableVersion.id == version_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="版本不存在")
    v.status = "published"
    v.published_at = datetime.now()
    db.commit()
    return GenericResponse(message="发布成功")


@router.delete("/versions/{version_id}", response_model=GenericResponse)
def delete_version(version_id: int, db: Session = Depends(get_db),
                   user: User = Depends(RoleRequired(["admin", "academic"]))):
    db.query(TimetableEntry).filter(TimetableEntry.version_id == version_id).delete()
    v = db.query(TimetableVersion).filter(TimetableVersion.id == version_id).first()
    if v:
        db.delete(v)
    db.commit()
    return GenericResponse(message="已删除")


@router.post("/versions/{version_id}/auto-schedule", response_model=GenericResponse)
def auto_schedule(version_id: int, db: Session = Depends(get_db),
                  user: User = Depends(RoleRequired(["admin", "academic"]))):
    v = db.query(TimetableVersion).filter(TimetableVersion.id == version_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="版本不存在")
    engine = SchedulingEngine(db, v.id, v.academic_year_id, v.semester_id)
    status, entries = engine.solve()
    count = engine.save_entries(entries)
    # 评分
    quality = QualityEvaluator(db, v.id).evaluate()
    v.quality_score = str(quality.get("total_score", 0))
    db.commit()
    return GenericResponse(data={"entries": count, "quality": quality})


@router.get("/entries", response_model=GenericResponse)
def get_entries(version_id: int, class_id: Optional[int] = None,
                teacher_id: Optional[int] = None,
                db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """获取课表条目。教师用户只能查看已发布版本。"""
    v = db.query(TimetableVersion).filter(TimetableVersion.id == version_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="版本不存在")
    if user.role_code == "teacher" and v.status != "published":
        raise HTTPException(status_code=403, detail="教师仅可查看已发布课表")

    subjects = {s.id: s for s in db.query(Subject).all()}
    teachers = {t.id: t for t in db.query(Teacher).all()}
    classes = {c.id: c for c in db.query(ClassInfo).all()}
    classrooms = {r.id: r for r in db.query(Classroom).all()}

    q = db.query(TimetableEntry).filter(TimetableEntry.version_id == version_id)
    if class_id:
        q = q.filter(TimetableEntry.class_id == class_id)
    if teacher_id:
        q = q.filter(TimetableEntry.teacher_id == teacher_id)
    entries = q.all()

    # 按班级分组 -> 按 day + slot_index 编排
    result = []
    for e in entries:
        s = subjects.get(e.subject_id)
        t = teachers.get(e.teacher_id)
        c = classes.get(e.class_id)
        r = classrooms.get(e.classroom_id)
        result.append({
            "id": e.id, "class_id": e.class_id, "subject_id": e.subject_id,
            "teacher_id": e.teacher_id, "classroom_id": e.classroom_id,
            "day_of_week": e.day_of_week, "time_slot_id": e.time_slot_id,
            "cycle_id": e.cycle_id, "is_fixed": e.is_fixed,
            "subject_name": s.name if s else "", "teacher_name": t.name if t else "",
            "class_name": c.name if c else "", "classroom_name": r.name if r else "",
            "schedule_plan_id": e.schedule_plan_id
        })
    return GenericResponse(data=result)


@router.post("/entries", response_model=GenericResponse)
def add_entry(version_id: int, payload: dict, db: Session = Depends(get_db),
              user: User = Depends(RoleRequired(["admin", "academic"]))):
    v = db.query(TimetableVersion).filter(TimetableVersion.id == version_id).first()
    if not v:
        raise HTTPException(status_code=404)
    conflicts = ConflictDetector(db).check_conflict(
        version_id=version_id,
        class_id=payload.get("class_id"), teacher_id=payload.get("teacher_id"),
        classroom_id=payload.get("classroom_id"),
        day_of_week=payload.get("day_of_week"),
        time_slot_id=payload.get("time_slot_id"),
        cycle_id=payload.get("cycle_id")
    )
    if conflicts:
        raise HTTPException(status_code=400, detail=f"存在冲突: {[c['reason'] for c in conflicts]}")
    e = TimetableEntry(
        version_id=version_id, academic_year_id=v.academic_year_id,
        semester_id=v.semester_id, **payload
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return GenericResponse(data={"id": e.id})


@router.post("/entries/{entry_id}/move", response_model=GenericResponse)
def move_entry(entry_id: int, payload: TimetableMoveRequest, db: Session = Depends(get_db),
               user: User = Depends(RoleRequired(["admin", "academic"]))):
    e = db.query(TimetableEntry).filter(TimetableEntry.id == entry_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="条目不存在")
    if e.is_fixed:
        raise HTTPException(status_code=400, detail="固定课程不可移动")
    conflicts = ConflictDetector(db).check_conflict(
        version_id=e.version_id,
        class_id=e.class_id, teacher_id=e.teacher_id,
        classroom_id=payload.to_classroom_id or e.classroom_id,
        day_of_week=payload.to_day,
        time_slot_id=payload.to_time_slot_id,
        cycle_id=e.cycle_id, exclude_entry_id=e.id
    )
    if conflicts:
        raise HTTPException(status_code=400, detail=f"存在冲突: {[c['reason'] for c in conflicts]}")
    e.day_of_week = payload.to_day
    e.time_slot_id = payload.to_time_slot_id
    if payload.to_classroom_id:
        e.classroom_id = payload.to_classroom_id
    db.add(AdjustmentRecord(
        version_id=e.version_id, academic_year_id=e.academic_year_id,
        semester_id=e.semester_id, operator_id=user.id, type="move",
        detail={"entry_id": e.id, "to_day": payload.to_day,
                "to_time_slot_id": payload.to_time_slot_id}
    ))
    db.commit()
    return GenericResponse(message="移动成功")


@router.post("/entries/swap", response_model=GenericResponse)
def swap_entries(payload: TimetableSwapRequest, db: Session = Depends(get_db),
                 user: User = Depends(RoleRequired(["admin", "academic"]))):
    a = db.query(TimetableEntry).filter(TimetableEntry.id == payload.entry_a_id).first()
    b = db.query(TimetableEntry).filter(TimetableEntry.id == payload.entry_b_id).first()
    if not a or not b:
        raise HTTPException(status_code=404, detail="条目不存在")
    if a.is_fixed or b.is_fixed:
        raise HTTPException(status_code=400, detail="含固定课程")
    # 交换 day/slot
    a_day, a_slot = a.day_of_week, a.time_slot_id
    a.day_of_week, a.time_slot_id = b.day_of_week, b.time_slot_id
    b.day_of_week, b.time_slot_id = a_day, a_slot
    db.add(AdjustmentRecord(
        version_id=a.version_id, academic_year_id=a.academic_year_id,
        semester_id=a.semester_id, operator_id=user.id, type="swap",
        detail={"entry_a": a.id, "entry_b": b.id}
    ))
    db.commit()
    return GenericResponse(message="交换成功")


@router.delete("/entries/{entry_id}", response_model=GenericResponse)
def delete_entry(entry_id: int, db: Session = Depends(get_db),
                 user: User = Depends(RoleRequired(["admin", "academic"]))):
    e = db.query(TimetableEntry).filter(TimetableEntry.id == entry_id).first()
    if not e:
        raise HTTPException(status_code=404)
    db.delete(e)
    db.commit()
    return GenericResponse(message="已删除")


@router.get("/versions/{version_id}/quality", response_model=GenericResponse)
def get_quality(version_id: int, db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    q = db.query(TimetableQuality).filter(TimetableQuality.version_id == version_id).order_by(
        TimetableQuality.id.desc()).first()
    if not q:
        return GenericResponse(data={"total_score": 0})
    return GenericResponse(data={
        "main_coverage_rate": q.main_coverage_rate,
        "teacher_balance_score": q.teacher_balance_score,
        "subject_balance_score": q.subject_balance_score,
        "room_utilization": q.room_utilization,
        "cycle_score": q.cycle_score,
        "consecutive_score": q.consecutive_score,
        "total_score": q.total_score
    })


# ---------- Export ----------
@router.get("/export/class/{class_id}/excel")
def export_class_excel(class_id: int, version_id: int, show_teacher: bool = True,
                       db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = ExportService(db, version_id).export_class_excel(class_id, show_teacher)
    return Response(content=data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f"attachment; filename=class_{class_id}.xlsx"})


@router.get("/export/class/{class_id}/pdf")
def export_class_pdf(class_id: int, version_id: int, show_teacher: bool = True,
                     db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = ExportService(db, version_id).export_class_pdf(class_id, show_teacher)
    return Response(content=data, media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename=class_{class_id}.pdf"})


@router.get("/export/teacher/{teacher_id}/excel")
def export_teacher_excel(teacher_id: int, version_id: int,
                         db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = ExportService(db, version_id).export_teacher_excel(teacher_id)
    return Response(content=data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f"attachment; filename=teacher_{teacher_id}.xlsx"})
