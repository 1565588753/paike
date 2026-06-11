from sqlalchemy import Column, BigInteger, String, Integer, SmallInteger, DateTime, Date, Boolean, Text
try:
    from sqlalchemy import JSON  # SQLAlchemy 2.0 通用 JSON
except Exception:  # pragma: no cover
    from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.sql import func
from app.core.database import Base


class AcademicYear(Base):
    __tablename__ = "academic_year"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_archived = Column(Boolean, default=False)
    is_current = Column(Boolean, default=False)
    remark = Column(String(255))
    created_at = Column(DateTime, default=func.now())


class Semester(Base):
    __tablename__ = "semester"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    academic_year_id = Column(BigInteger, nullable=False)
    name = Column(String(32), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_weeks = Column(Integer, default=20)
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


class Subject(Base):
    __tablename__ = "subject"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    code = Column(String(32), unique=True, nullable=False)
    is_main = Column(Boolean, default=False)
    need_room = Column(Boolean, default=False)
    color = Column(String(16), default="#409EFF")
    sort_order = Column(Integer, default=0)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=func.now())


class Teacher(Base):
    __tablename__ = "teacher"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    teacher_no = Column(String(32), unique=True, nullable=False)
    name = Column(String(64), nullable=False)
    gender = Column(String(8), default="male")
    phone = Column(String(32))
    title = Column(String(64))
    main_subject_id = Column(BigInteger)
    subject_ids = Column(JSON)
    max_weekly_hours = Column(Integer, default=20)
    max_daily_hours = Column(Integer, default=4)
    forbid_slots = Column(JSON)
    status = Column(SmallInteger, default=1)
    remark = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Grade(Base):
    __tablename__ = "grade"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    level = Column(Integer, nullable=False)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=func.now())


class ClassInfo(Base):
    __tablename__ = "class_info"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    grade_id = Column(BigInteger, nullable=False)
    student_count = Column(Integer, default=40)
    schedule_plan_id = Column(BigInteger)
    academic_year_id = Column(BigInteger, nullable=False)
    remark = Column(String(255))
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=func.now())


class Classroom(Base):
    __tablename__ = "classroom"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    type = Column(String(32), default="normal")
    capacity = Column(Integer, default=45)
    subject_ids = Column(JSON)
    location = Column(String(128))
    status = Column(SmallInteger, default=1)
    remark = Column(String(255))
    created_at = Column(DateTime, default=func.now())


class SchedulePlan(Base):
    __tablename__ = "schedule_plan"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(String(255))
    is_default = Column(Boolean, default=False)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=func.now())


class TimeSlot(Base):
    __tablename__ = "time_slot"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    schedule_plan_id = Column(BigInteger, nullable=False)
    period_no = Column(Integer, nullable=False)
    period_name = Column(String(32), nullable=False)
    start_time = Column(String(16), nullable=False)
    end_time = Column(String(16), nullable=False)
    is_break = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)


class CourseCycle(Base):
    __tablename__ = "course_cycle"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String(32), unique=True, nullable=False)
    name = Column(String(64), nullable=False)
    week_mask = Column(String(32), default="11111111111111111111")
    created_at = Column(DateTime, default=func.now())


class HRRecord(Base):
    __tablename__ = "hr_record"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    academic_year_id = Column(BigInteger, nullable=False)
    semester_id = Column(BigInteger, nullable=False)
    class_id = Column(BigInteger, nullable=False)
    head_teacher_id = Column(BigInteger)
    subject_teachers = Column(JSON, nullable=False)
    remark = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class TimetableVersion(Base):
    __tablename__ = "timetable_version"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    academic_year_id = Column(BigInteger, nullable=False)
    semester_id = Column(BigInteger, nullable=False)
    version_no = Column(String(32), nullable=False)
    version_name = Column(String(128))
    status = Column(String(16), default="draft")
    published_at = Column(DateTime)
    remark = Column(String(255))
    quality_score = Column(String(16))
    created_by = Column(BigInteger)
    created_at = Column(DateTime, default=func.now())


class TimetableEntry(Base):
    __tablename__ = "timetable_entry"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    version_id = Column(BigInteger, nullable=False)
    academic_year_id = Column(BigInteger, nullable=False)
    semester_id = Column(BigInteger, nullable=False)
    class_id = Column(BigInteger, nullable=False)
    subject_id = Column(BigInteger, nullable=False)
    teacher_id = Column(BigInteger, nullable=False)
    classroom_id = Column(BigInteger)
    day_of_week = Column(Integer, nullable=False)
    time_slot_id = Column(BigInteger, nullable=False)
    schedule_plan_id = Column(BigInteger, nullable=False)
    cycle_id = Column(BigInteger, nullable=False)
    is_fixed = Column(Boolean, default=False)
    remark = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class SwapRequest(Base):
    __tablename__ = "swap_request"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    version_id = Column(BigInteger, nullable=False)
    academic_year_id = Column(BigInteger, nullable=False)
    semester_id = Column(BigInteger, nullable=False)
    requester_teacher_id = Column(BigInteger, nullable=False)
    target_teacher_id = Column(BigInteger, nullable=False)
    entry_a_id = Column(BigInteger, nullable=False)
    entry_b_id = Column(BigInteger)
    type = Column(String(16), default="swap")
    reason = Column(String(500))
    status = Column(String(16), default="pending")
    requested_at = Column(DateTime, default=func.now())
    confirmed_at = Column(DateTime)
    approved_at = Column(DateTime)
    approved_by = Column(BigInteger)
    effective_at = Column(Date)
    remark = Column(String(255))


class AdjustmentRecord(Base):
    __tablename__ = "adjustment_record"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    version_id = Column(BigInteger, nullable=False)
    academic_year_id = Column(BigInteger, nullable=False)
    semester_id = Column(BigInteger, nullable=False)
    operator_id = Column(BigInteger, nullable=False)
    type = Column(String(16), nullable=False)
    detail = Column(JSON)
    operator_note = Column(String(500))
    created_at = Column(DateTime, default=func.now())


class SpecialDate(Base):
    __tablename__ = "special_date"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    academic_year_id = Column(BigInteger, nullable=False)
    semester_id = Column(BigInteger)
    date = Column(Date, nullable=False)
    type = Column(String(16), nullable=False)
    name = Column(String(128), nullable=False)
    remark = Column(String(255))
    created_at = Column(DateTime, default=func.now())


class Notification(Base):
    __tablename__ = "notification"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    recipient_user_id = Column(BigInteger, nullable=False)
    type = Column(String(32), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    related_id = Column(BigInteger)
    related_type = Column(String(32))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


class TimetableQuality(Base):
    __tablename__ = "timetable_quality"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    version_id = Column(BigInteger, nullable=False)
    main_coverage_rate = Column(String(16))
    teacher_balance_score = Column(String(16))
    subject_balance_score = Column(String(16))
    room_utilization = Column(String(16))
    cycle_score = Column(String(16))
    consecutive_score = Column(String(16))
    total_score = Column(String(16))
    detail = Column(JSON)
    created_at = Column(DateTime, default=func.now())


class SubjectWeeklyPlan(Base):
    __tablename__ = "subject_weekly_plan"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    academic_year_id = Column(BigInteger, nullable=False)
    semester_id = Column(BigInteger, nullable=False)
    class_id = Column(BigInteger, nullable=False)
    subject_id = Column(BigInteger, nullable=False)
    weekly_hours = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
