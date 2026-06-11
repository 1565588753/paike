from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from .core.database import Base, engine, DATABASE_URL, SessionLocal
from .core.config import settings
from .api.v1.endpoints import auth, teachers, basic, years, hr, timetable, swap, stats, system


def create_tables_and_seed():
    """启动时自动建表 (SQLite无表不存在则创建)。同时插入初始演示数据。"""
    # 先导入所有模型以便 SQLAlchemy 感知它们
    from .models import user as _models  # noqa: F401
    from .models import scheduling as _sched  # noqa: F401
    from .models import log as _log  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # 初始数据: 仅在表已创建后插入
    db = SessionLocal()
    try:
        from .models.user import User, Role, Permission, RolePermission
        from .models.scheduling import (
            AcademicYear, Semester, Subject, Teacher, Grade, ClassInfo,
            Classroom, SchedulePlan, TimeSlot, CourseCycle
        )
        from passlib.context import CryptContext
        pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
        default_pwd = pwd.hash("123456")

        # 角色
        for code, name, desc in [
            ("admin", "系统管理员", "拥有全部权限"),
            ("academic", "教务管理员", "管理教务数据与排课"),
            ("teacher", "教师", "查看课表与发起换课"),
            ("leader", "校领导", "查看统计报表"),
        ]:
            if not db.query(Role).filter(Role.role_code == code).first():
                db.add(Role(role_code=code, role_name=name, description=desc))
        db.commit()

        # 管理员账号
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(username="admin", password_hash=default_pwd, real_name="系统管理员",
                    role_code="admin", first_login=False, status=1))
        if not db.query(User).filter(User.username == "academic01").first():
            db.add(User(username="academic01", password_hash=default_pwd, real_name="张教务",
                    role_code="academic", first_login=False, status=1))

        # 年级
        grades = {}
        for lvl, gname in [(1, "一年级"), (2, "二年级"), (3, "三年级"), (4, "四年级"), (5, "五年级"), (6, "六年级")]:
            g = db.query(Grade).filter(Grade.level == lvl).first()
            if not g:
                g = Grade(name=gname, level=lvl, status=1)
                db.add(g)
                db.flush()
            grades[lvl] = g.id
        db.commit()

        # 科目
        subjects = {}
        subj_list = [
            ("语文", "chinese", 1, 0, "#E74C3C", 1),
            ("数学", "math", 1, 0, "#3498DB", 2),
            ("英语", "english", 1, 0, "#27AE60", 3),
            ("道法", "daofa", 0, 0, "#8E44AD", 4),
            ("科学", "science", 0, 1, "#16A085", 5),
            ("信息科技", "it", 0, 1, "#2C3E50", 6),
            ("音乐", "music", 0, 1, "#E67E22", 7),
            ("体育", "sport", 0, 1, "#F39C12", 8),
            ("美术", "art", 0, 1, "#D35400", 9),
            ("劳动", "labor", 0, 0, "#7F8C8D", 10),
            ("心理", "psychology", 0, 0, "#9B59B6", 11),
            ("健康", "health", 0, 0, "#1ABC9C", 12),
            ("综合实践", "practice", 0, 0, "#34495E", 13),
            ("校本课程", "schoolbased", 0, 0, "#C0392B", 14),
            ("阅读课", "reading", 0, 0, "#2980B9", 15),
            ("自习课", "selfstudy", 0, 0, "#95A5A6", 16),
        ]
        for name, code, is_main, need_room, color, sort in subj_list:
            s = db.query(Subject).filter(Subject.code == code).first()
            if not s:
                s = Subject(name=name, code=code, is_main=is_main, need_room=need_room,
                             color=color, sort_order=sort, status=1)
                db.add(s)
                db.flush()
            subjects[code] = s.id
        db.commit()

        # 课程周期
        for code, name, mask in [
            ("ALL", "每周", "1" * 20),
            ("ODD", "单周", "10" * 10),
            ("EVEN", "双周", "01" * 10),
        ]:
            if not db.query(CourseCycle).filter(CourseCycle.code == code).first():
                db.add(CourseCycle(code=code, name=name, week_mask=mask))
        db.commit()

        # 作息方案
        plan1 = db.query(SchedulePlan).filter(SchedulePlan.name == "低年级作息").first()
        if not plan1:
            plan1 = SchedulePlan(name="低年级作息", description="一、二年级", is_default=1, status=1)
            db.add(plan1)
            db.flush()
            _add_slots(db, plan1.id, [
                (1, "第一节", "08:00", "08:35", 0, 1),
                (2, "第二节", "08:45", "09:20", 0, 2),
                (0, "课间操", "09:20", "09:40", 1, 3),
                (3, "第三节", "09:40", "10:15", 0, 4),
                (4, "第四节", "10:25", "11:00", 0, 5),
                (0, "午休", "11:00", "14:00", 1, 6),
                (5, "第五节", "14:00", "14:35", 0, 7),
                (6, "第六节", "14:45", "15:20", 0, 8),
                (7, "第七节", "15:30", "16:05", 0, 9),
            ])

        plan2 = db.query(SchedulePlan).filter(SchedulePlan.name == "中高年级作息").first()
        if not plan2:
            plan2 = SchedulePlan(name="中高年级作息", description="三至六年级", is_default=0, status=1)
            db.add(plan2)
            db.flush()
            _add_slots(db, plan2.id, [
                (1, "第一节", "08:00", "08:40", 0, 1),
                (2, "第二节", "08:50", "09:30", 0, 2),
                (0, "课间操", "09:30", "09:50", 1, 3),
                (3, "第三节", "09:50", "10:30", 0, 4),
                (4, "第四节", "10:40", "11:20", 0, 5),
                (0, "午休", "11:20", "14:00", 1, 6),
                (5, "第五节", "14:00", "14:40", 0, 7),
                (6, "第六节", "14:50", "15:30", 0, 8),
                (7, "第七节", "15:40", "16:20", 0, 9),
            ])
        db.commit()

        # 学年/学期
        ay = db.query(AcademicYear).filter(AcademicYear.name == "2024-2025").first()
        if not ay:
            ay = AcademicYear(name="2024-2025", start_date="2024-09-01", end_date="2025-07-15",
                           is_current=1, is_archived=0)
            db.add(ay)
            db.flush()
            for sname, sdate, edate in [("第一学期", "2024-09-01", "2025-01-20"),
                                         ("第二学期", "2025-02-20", "2025-07-15")]:
                db.add(Semester(academic_year_id=ay.id, name=sname,
                                 start_date=sdate, end_date=edate,
                                 total_weeks=20, is_current=(sname == "第一学期")))
        db.commit()

        # 示例教师
        demo_teachers = [
            ("T2024001", "张老师", "female", "小学高级教师"),
            ("T2024002", "李老师", "female", "小学高级教师"),
            ("T2024003", "王老师", "male", "小学一级教师"),
            ("T2024004", "赵老师", "male", "小学一级教师"),
        ]
        teacher_ids = {}
        for no, name, gender, title in demo_teachers:
            t = db.query(Teacher).filter(Teacher.teacher_no == no).first()
            if not t:
                t = Teacher(teacher_no=no, name=name, gender=gender, title=title,
                            main_subject_id=subjects.get("chinese"), subject_ids=None,
                            max_weekly_hours=20, max_daily_hours=4, status=1)
                db.add(t)
                db.flush()
            teacher_ids[no] = t.id
            # 对应账号
            if not db.query(User).filter(User.username == no).first():
                db.add(User(username=no, password_hash=default_pwd, real_name=name,
                            role_code="teacher", teacher_id=t.id, first_login=True, status=1))
        db.commit()

        # 示例教室 + 班级
        ay2 = db.query(AcademicYear).filter(AcademicYear.name == "2024-2025").first()
        plan_low = db.query(SchedulePlan).filter(SchedulePlan.name == "低年级作息").first()
        plan_high = db.query(SchedulePlan).filter(SchedulePlan.name == "中高年级作息").first()
        for lvl, class_names in [
            (1, ["一(1)班", "一(2)班"]),
            (2, ["二(1)班"]),
            (3, ["三(1)班"]),
        ]:
            for cname in class_names:
                if not db.query(ClassInfo).filter(
                    ClassInfo.name == cname,
                    ClassInfo.academic_year_id == ay2.id
                ).first():
                    pid = plan_low.id if lvl <= 2 else (plan_high.id if plan_high else plan_low.id)
                    db.add(ClassInfo(name=cname, grade_id=grades[lvl], student_count=40,
                                      schedule_plan_id=pid, academic_year_id=ay2.id, status=1))
        db.commit()

        # 示例教室
        for cname in ["微机室", "音乐教室", "美术教室", "科学实验室", "操场"]:
            if not db.query(Classroom).filter(Classroom.name == cname).first():
                db.add(Classroom(name=cname, type="normal", capacity=45, status=1))
        db.commit()
        print(f"[seed] 初始数据已准备完成 (数据库: {DATABASE_URL})")
    except Exception as e:
        print(f"[seed] 跳过或失败: {e}")
        db.rollback()
    finally:
        db.close()


def _add_slots(db, plan_id, slots):
    for pno, pname, st, et, isbr, sorter in slots:
        db.add(TimeSlot(schedule_plan_id=plan_id, period_no=pno, period_name=pname,
                       start_time=st, end_time=et, is_break=isbr, sort_order=sorter))


app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 启动任务: 建表并插入初始数据 (重复执行安全)
create_tables_and_seed()


@app.get("/", tags=["系统"])
def root():
    return {"message": settings.APP_NAME, "docs": "/docs", "db": DATABASE_URL}


prefix = "/api/v1"
app.include_router(auth.router, prefix=prefix)
app.include_router(teachers.router, prefix=prefix)
app.include_router(basic.router, prefix=prefix)
app.include_router(years.router, prefix=prefix + "/years")
app.include_router(hr.router, prefix=prefix)
app.include_router(timetable.router, prefix=prefix + "/timetable")
app.include_router(swap.router, prefix=prefix + "/swaps")
app.include_router(stats.router, prefix=prefix)
app.include_router(system.router, prefix=prefix)
