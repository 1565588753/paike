from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    real_name: str
    role_code: str
    first_login: bool
    teacher_id: Optional[int] = None


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


class UserInfoResponse(BaseModel):
    id: int
    username: str
    real_name: str
    role_code: str
    teacher_id: Optional[int] = None
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Teacher ----------
class TeacherBase(BaseModel):
    teacher_no: str
    name: str
    gender: str = "male"
    phone: Optional[str] = None
    title: Optional[str] = None
    main_subject_id: Optional[int] = None
    subject_ids: Optional[List[int]] = None
    max_weekly_hours: int = 20
    max_daily_hours: int = 4
    forbid_slots: Optional[Any] = None
    status: int = 1
    remark: Optional[str] = None


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(TeacherBase):
    pass


class TeacherResponse(TeacherBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Class ----------
class ClassInfoBase(BaseModel):
    name: str
    grade_id: int
    student_count: int = 40
    schedule_plan_id: Optional[int] = None
    academic_year_id: int
    remark: Optional[str] = None
    status: int = 1


class ClassInfoResponse(ClassInfoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Subject ----------
class SubjectBase(BaseModel):
    name: str
    code: str
    is_main: bool = False
    need_room: bool = False
    color: str = "#409EFF"
    sort_order: int = 0


class SubjectResponse(SubjectBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Classroom ----------
class ClassroomBase(BaseModel):
    name: str
    type: str = "normal"
    capacity: int = 45
    subject_ids: Optional[List[int]] = None
    location: Optional[str] = None
    status: int = 1
    remark: Optional[str] = None


class ClassroomResponse(ClassroomBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Year/Semester ----------
class YearResponse(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: date
    is_archived: bool
    is_current: bool

    class Config:
        from_attributes = True


class SemesterResponse(BaseModel):
    id: int
    academic_year_id: int
    name: str
    start_date: date
    end_date: date
    total_weeks: int
    is_current: bool

    class Config:
        from_attributes = True


# ---------- HR ----------
class HRRecordBase(BaseModel):
    academic_year_id: int
    semester_id: int
    class_id: int
    head_teacher_id: Optional[int] = None
    subject_teachers: Dict[str, int] = {}
    remark: Optional[str] = None


class HRRecordResponse(HRRecordBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Timetable ----------
class TimetableEntryBase(BaseModel):
    class_id: int
    subject_id: int
    teacher_id: int
    classroom_id: Optional[int] = None
    day_of_week: int
    time_slot_id: int
    schedule_plan_id: int
    cycle_id: int
    is_fixed: bool = False
    remark: Optional[str] = None


class TimetableEntryResponse(TimetableEntryBase):
    id: int
    subject_name: Optional[str] = None
    teacher_name: Optional[str] = None
    classroom_name: Optional[str] = None
    class_name: Optional[str] = None
    cycle_code: Optional[str] = None

    class Config:
        from_attributes = True


class TimetableMoveRequest(BaseModel):
    entry_id: int
    to_day: int
    to_time_slot_id: int
    to_classroom_id: Optional[int] = None


class TimetableSwapRequest(BaseModel):
    entry_a_id: int
    entry_b_id: int


class SwapRequestCreate(BaseModel):
    entry_a_id: int
    target_teacher_id: int
    entry_b_id: Optional[int] = None
    reason: Optional[str] = None


# ---------- Generic ----------
class PageResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Any]


class GenericResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None
