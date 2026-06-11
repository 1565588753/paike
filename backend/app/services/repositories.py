from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
from ..models.scheduling import (
    AcademicYear, Semester, Subject, Teacher, Grade, ClassInfo,
    Classroom, SchedulePlan, TimeSlot, CourseCycle, HRRecord,
    TimetableVersion, TimetableEntry, SwapRequest, AdjustmentRecord,
    SpecialDate, TimetableQuality, SubjectWeeklyPlan
)
from ..models.user import User, Role, Permission, RolePermission
from ..models.log import OperationLog
from datetime import datetime


class BaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, model, data: dict):
        instance = model(**data)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def update(self, instance, data: dict):
        for k, v in data.items():
            setattr(instance, k, v)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, instance):
        self.db.delete(instance)
        self.db.commit()


class UserRepository(BaseRepository):
    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def list(self, skip=0, limit=100):
        return self.db.query(User).offset(skip).limit(limit).all()


class TeacherRepository(BaseRepository):
    def list(self, keyword: str = None, skip=0, limit=100):
        q = self.db.query(Teacher).filter(Teacher.status == 1)
        if keyword:
            q = q.filter(Teacher.name.contains(keyword) | Teacher.teacher_no.contains(keyword))
        return q.order_by(Teacher.teacher_no).offset(skip).limit(limit).all()

    def count(self, keyword: str = None):
        q = self.db.query(Teacher).filter(Teacher.status == 1)
        if keyword:
            q = q.filter(Teacher.name.contains(keyword) | Teacher.teacher_no.contains(keyword))
        return q.count()

    def get_by_no(self, no: str):
        return self.db.query(Teacher).filter(Teacher.teacher_no == no).first()


class ClassRepository(BaseRepository):
    def list(self, academic_year_id: int = None, grade_id: int = None):
        q = self.db.query(ClassInfo)
        if academic_year_id:
            q = q.filter(ClassInfo.academic_year_id == academic_year_id)
        if grade_id:
            q = q.filter(ClassInfo.grade_id == grade_id)
        return q.order_by(ClassInfo.name).all()


class SubjectRepository(BaseRepository):
    def all(self):
        return self.db.query(Subject).filter(Subject.status == 1).order_by(Subject.sort_order).all()


class ClassroomRepository(BaseRepository):
    def list(self, type: str = None):
        q = self.db.query(Classroom).filter(Classroom.status == 1)
        if type:
            q = q.filter(Classroom.type == type)
        return q.order_by(Classroom.name).all()


class SchedulePlanRepository(BaseRepository):
    def all(self):
        return self.db.query(SchedulePlan).all()

    def get_slots(self, plan_id: int):
        return self.db.query(TimeSlot).filter(TimeSlot.schedule_plan_id == plan_id).order_by(TimeSlot.sort_order).all()


class YearRepository(BaseRepository):
    def get_current(self):
        return self.db.query(AcademicYear).filter(AcademicYear.is_current == True).first()

    def all(self):
        return self.db.query(AcademicYear).order_by(AcademicYear.name.desc()).all()

    def get_semesters(self, year_id: int):
        return self.db.query(Semester).filter(Semester.academic_year_id == year_id).all()


class HRRepository(BaseRepository):
    def list(self, academic_year_id: int, semester_id: int):
        return self.db.query(HRRecord).filter(
            HRRecord.academic_year_id == academic_year_id,
            HRRecord.semester_id == semester_id
        ).all()

    def get_by_class(self, class_id: int, semester_id: int):
        return self.db.query(HRRecord).filter(
            HRRecord.class_id == class_id,
            HRRecord.semester_id == semester_id
        ).first()


class CycleRepository(BaseRepository):
    def all(self):
        return self.db.query(CourseCycle).all()


class TimetableRepository(BaseRepository):
    def create_version(self, academic_year_id: int, semester_id: int, version_name: str = None, created_by: int = None):
        max_v = self.db.query(TimetableVersion).filter(
            TimetableVersion.academic_year_id == academic_year_id,
            TimetableVersion.semester_id == semester_id
        ).count()
        v = TimetableVersion(
            academic_year_id=academic_year_id,
            semester_id=semester_id,
            version_no=f"V{max_v + 1:03d}",
            version_name=version_name or f"V{max_v + 1:03d}",
            status="draft",
            created_by=created_by
        )
        self.db.add(v)
        self.db.commit()
        self.db.refresh(v)
        return v

    def list_versions(self, academic_year_id: int, semester_id: int):
        return self.db.query(TimetableVersion).filter(
            TimetableVersion.academic_year_id == academic_year_id,
            TimetableVersion.semester_id == semester_id
        ).order_by(TimetableVersion.created_at.desc()).all()

    def publish_version(self, version_id: int):
        # 先将其它版本改为非发布
        self.db.query(TimetableVersion).filter(
            TimetableVersion.id != version_id,
            TimetableVersion.status == "published"
        ).update({TimetableVersion.status: "draft"})
        v = self.db.query(TimetableVersion).filter(TimetableVersion.id == version_id).first()
        if v:
            v.status = "published"
            v.published_at = datetime.now()
        self.db.commit()

    def get_entries(self, version_id: int, class_id: int = None, teacher_id: int = None):
        q = self.db.query(TimetableEntry).filter(TimetableEntry.version_id == version_id)
        if class_id:
            q = q.filter(TimetableEntry.class_id == class_id)
        if teacher_id:
            q = q.filter(TimetableEntry.teacher_id == teacher_id)
        return q.all()

    def add_entry(self, entry_data: dict, version_id: int, academic_year_id: int, semester_id: int):
        e = TimetableEntry(**entry_data, version_id=version_id,
                           academic_year_id=academic_year_id, semester_id=semester_id)
        self.db.add(e)
        self.db.commit()
        self.db.refresh(e)
        return e

    def clear_entries(self, version_id: int):
        self.db.query(TimetableEntry).filter(TimetableEntry.version_id == version_id).delete()
        self.db.commit()

    def delete_version(self, version_id: int):
        self.clear_entries(version_id)
        self.db.query(TimetableVersion).filter(TimetableVersion.id == version_id).delete()
        self.db.commit()


class SwapRepository(BaseRepository):
    def create_request(self, version_id: int, academic_year_id: int, semester_id: int,
                       requester_teacher_id: int, target_teacher_id: int,
                       entry_a_id: int, entry_b_id: int = None, reason: str = None):
        r = SwapRequest(
            version_id=version_id, academic_year_id=academic_year_id, semester_id=semester_id,
            requester_teacher_id=requester_teacher_id, target_teacher_id=target_teacher_id,
            entry_a_id=entry_a_id, entry_b_id=entry_b_id, reason=reason, status="pending"
        )
        self.db.add(r)
        self.db.commit()
        self.db.refresh(r)
        return r

    def list_by_teacher(self, teacher_id: int, status: str = None):
        q = self.db.query(SwapRequest).filter(
            (SwapRequest.requester_teacher_id == teacher_id) |
            (SwapRequest.target_teacher_id == teacher_id)
        )
        if status:
            q = q.filter(SwapRequest.status == status)
        return q.order_by(SwapRequest.requested_at.desc()).all()

    def list_pending(self):
        return self.db.query(SwapRequest).filter(SwapRequest.status == "pending").order_by(SwapRequest.requested_at.desc()).all()


class NotificationRepository(BaseRepository):
    def send(self, user_id: int, type: str, title: str, content: str = None, related_id: int = None):
        n = type.__class__
        n = Notification.__mro__[0]
        from ..models.scheduling import Notification as N
        inst = N(recipient_user_id=user_id, type=type, title=title, content=content, related_id=related_id)
        self.db.add(inst)
        self.db.commit()

    def list_by_user(self, user_id: int, is_read: bool = None, limit=50):
        from ..models.scheduling import Notification as N
        q = self.db.query(N).filter(N.recipient_user_id == user_id)
        if is_read is not None:
            q = q.filter(N.is_read == is_read)
        return q.order_by(N.created_at.desc()).limit(limit).all()

    def mark_read(self, notification_id: int, user_id: int):
        from ..models.scheduling import Notification as N
        n = self.db.query(N).filter(N.id == notification_id, N.recipient_user_id == user_id).first()
        if n:
            n.is_read = True
            self.db.commit()
