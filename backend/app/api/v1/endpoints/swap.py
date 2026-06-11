from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user, RoleRequired
from app.models.user import User
from app.models.scheduling import SwapRequest, TimetableEntry, Notification
from app.schemas.common import SwapRequestCreate, GenericResponse

router = APIRouter(tags=["换课申请"])


@router.get("", response_model=GenericResponse)
def list_swaps(status: str = None, db: Session = Depends(get_db),
               user: User = Depends(get_current_user)):
    """教师看自己的；教务看所有。"""
    q = db.query(SwapRequest)
    if user.role_code == "teacher" and user.teacher_id:
        q = q.filter((SwapRequest.requester_teacher_id == user.teacher_id) |
                     (SwapRequest.target_teacher_id == user.teacher_id))
    if status:
        q = q.filter(SwapRequest.status == status)
    items = q.order_by(SwapRequest.requested_at.desc()).all()
    return GenericResponse(data=[{"id": s.id, "entry_a_id": s.entry_a_id, "entry_b_id": s.entry_b_id,
                                  "requester_teacher_id": s.requester_teacher_id,
                                  "target_teacher_id": s.target_teacher_id,
                                  "status": s.status, "reason": s.reason,
                                  "requested_at": s.requested_at.isoformat() if s.requested_at else None}
                                 for s in items])


@router.post("", response_model=GenericResponse)
def create_swap(payload: SwapRequestCreate, db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    if user.role_code != "teacher" or not user.teacher_id:
        raise HTTPException(status_code=403, detail="需教师账号")
    entry_a = db.query(TimetableEntry).filter(TimetableEntry.id == payload.entry_a_id).first()
    if not entry_a or entry_a.teacher_id != user.teacher_id:
        raise HTTPException(status_code=400, detail="非本人课程, 不可申请")
    req = SwapRequest(
        version_id=entry_a.version_id, academic_year_id=entry_a.academic_year_id,
        semester_id=entry_a.semester_id,
        requester_teacher_id=user.teacher_id,
        target_teacher_id=payload.target_teacher_id,
        entry_a_id=payload.entry_a_id, entry_b_id=payload.entry_b_id,
        reason=payload.reason, status="pending"
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    # 通知对方
    target_user = db.query(User).filter(User.teacher_id == payload.target_teacher_id).first()
    if target_user:
        n = Notification(recipient_user_id=target_user.id, type="swap",
                         title=f"收到换课申请 - {user.real_name}",
                         content=payload.reason or "", related_id=req.id)
        db.add(n)
        db.commit()
    return GenericResponse(data={"id": req.id}, message="申请已提交")


@router.post("/{swap_id}/confirm", response_model=GenericResponse)
def confirm_swap(swap_id: int, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    s = db.query(SwapRequest).filter(SwapRequest.id == swap_id).first()
    if not s:
        raise HTTPException(status_code=404)
    if user.role_code == "teacher" and s.target_teacher_id != user.teacher_id:
        raise HTTPException(status_code=403, detail="无权确认")
    s.status = "approved"
    s.confirmed_at = datetime.now()
    # 交换条目
    a = db.query(TimetableEntry).filter(TimetableEntry.id == s.entry_a_id).first()
    b = db.query(TimetableEntry).filter(TimetableEntry.id == s.entry_b_id).first() if s.entry_b_id else None
    if a and b:
        a_day, a_slot, a_teacher = a.day_of_week, a.time_slot_id, a.teacher_id
        a.day_of_week, a.time_slot_id, a.teacher_id = b.day_of_week, b.time_slot_id, b.teacher_id
        b.day_of_week, b.time_slot_id, b.teacher_id = a_day, a_slot, a_teacher
    db.commit()
    return GenericResponse(message="换课已确认")


@router.post("/{swap_id}/reject", response_model=GenericResponse)
def reject_swap(swap_id: int, db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    s = db.query(SwapRequest).filter(SwapRequest.id == swap_id).first()
    if not s:
        raise HTTPException(status_code=404)
    if user.role_code == "teacher" and s.target_teacher_id != user.teacher_id and s.requester_teacher_id != user.teacher_id:
        raise HTTPException(status_code=403)
    s.status = "rejected"
    db.commit()
    return GenericResponse(message="已拒绝")


@router.post("/{swap_id}/approve", response_model=GenericResponse)
def approve_swap(swap_id: int, db: Session = Depends(get_db),
                 user: User = Depends(RoleRequired(["admin", "academic"]))):
    s = db.query(SwapRequest).filter(SwapRequest.id == swap_id).first()
    if not s:
        raise HTTPException(status_code=404)
    s.status = "approved"
    s.approved_at = datetime.now()
    s.approved_by = user.id
    db.commit()
    return GenericResponse(message="审批通过")
