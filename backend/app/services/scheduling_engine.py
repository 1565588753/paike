from ortools.sat.python import cp_model
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
from ..models.scheduling import (
    Teacher, ClassInfo, Subject, Classroom, TimeSlot, SchedulePlan,
    HRRecord, TimetableEntry, TimetableVersion, SubjectWeeklyPlan, CourseCycle
)
from ..core.logger import logger
from datetime import datetime


class SchedulingEngine:
    """基于 Google OR-Tools 的自动排课引擎。"""

    def __init__(self, db: Session, version_id: int, academic_year_id: int, semester_id: int):
        self.db = db
        self.version_id = version_id
        self.academic_year_id = academic_year_id
        self.semester_id = semester_id
        self.classes: List[ClassInfo] = []
        self.teachers: Dict[int, Teacher] = {}
        self.subjects: Dict[int, Subject] = {}
        self.classrooms: Dict[int, Classroom] = {}
        self.time_slots: Dict[int, List[TimeSlot]] = {}  # plan_id -> slots
        self.hr_records: Dict[int, HRRecord] = {}  # class_id -> HRRecord
        self.weekly_hours: Dict[Tuple[int, int], int] = {}  # (class_id, subject_id) -> hours
        self.cycles: List[CourseCycle] = []

    def load_data(self):
        logger.info("加载排课基础数据...")
        self.classes = self.db.query(ClassInfo).filter(
            ClassInfo.academic_year_id == self.academic_year_id,
            ClassInfo.status == 1
        ).all()
        for t in self.db.query(Teacher).all():
            self.teachers[t.id] = t
        for s in self.db.query(Subject).all():
            self.subjects[s.id] = s
        for c in self.db.query(Classroom).all():
            self.classrooms[c.id] = c
        for plan in self.db.query(SchedulePlan).all():
            self.time_slots[plan.id] = self.db.query(TimeSlot).filter(
                TimeSlot.schedule_plan_id == plan.id,
                TimeSlot.is_break == False
            ).order_by(TimeSlot.sort_order).all()
        for hr in self.db.query(HRRecord).filter(
            HRRecord.academic_year_id == self.academic_year_id,
            HRRecord.semester_id == self.semester_id
        ).all():
            self.hr_records[hr.class_id] = hr
        for wp in self.db.query(SubjectWeeklyPlan).filter(
            SubjectWeeklyPlan.academic_year_id == self.academic_year_id,
            SubjectWeeklyPlan.semester_id == self.semester_id
        ).all():
            self.weekly_hours[(wp.class_id, wp.subject_id)] = wp.weekly_hours
        self.cycles = self.db.query(CourseCycle).all()
        logger.info(f"加载完成: 班级{len(self.classes)}, 教师{len(self.teachers)}, 科目{len(self.subjects)}")

    def get_default_hours(self, class_id: int, subject_id: int) -> int:
        """若无周课时配置，根据科目与年级提供默认值。"""
        key = (class_id, subject_id)
        if key in self.weekly_hours:
            return self.weekly_hours[key]
        subj = self.subjects.get(subject_id)
        if not subj:
            return 0
        if subj.is_main:
            return 5  # 主科默认5节
        if subj.code in ("sport", "music", "art"):
            return 2
        if subj.code in ("science", "daofa"):
            return 2
        return 1

    def solve(self) -> Tuple[int, List[dict]]:
        """执行排课。返回 (status, entries)"""
        self.load_data()

        model = cp_model.CpModel()
        days = [1, 2, 3, 4, 5]  # 周一到周五

        # 为每个 (班级, 科目, 节次索引) 建立布尔变量
        # class_subj_period_vars[(c, s, day, slot_idx)] = BoolVar
        # 同时建立 teacher 占用变量，确保冲突约束
        class_subj_period_vars = {}
        all_scheduled = []

        # 构建每个班级需要的科目与节数
        tasks = []  # (class_id, subject_id, teacher_id, hours)
        for c in self.classes:
            hr = self.hr_records.get(c.id)
            if not hr:
                continue
            subj_teachers = hr.subject_teachers or {}
            if isinstance(subj_teachers, dict):
                for subj_id_str, teacher_id in subj_teachers.items():
                    try:
                        subj_id = int(subj_id_str) if isinstance(subj_id_str, str) else int(subj_id_str)
                    except (ValueError, TypeError):
                        continue
                    hours = self.get_default_hours(c.id, subj_id)
                    if hours > 0 and int(teacher_id) in self.teachers:
                        tasks.append((c.id, subj_id, int(teacher_id), hours))

        # 获取班级作息方案
        def get_slots_for_class(c):
            plan_id = c.schedule_plan_id or 1
            return self.time_slots.get(plan_id, [])

        # 每个任务 -> hours个时段变量
        task_vars = {}  # (task_idx, day, slot_idx) -> BoolVar
        teacher_occ = {}  # (teacher_id, day, slot_idx) -> list of vars to sum <= 1
        class_occ = {}  # (class_id, day, slot_idx) -> list of vars to sum <= 1
        room_occ = {}  # (room_id, day, slot_idx) -> list

        main_subject_ids = [s.id for s in self.subjects.values() if s.is_main]
        sport_subject_ids = [s.id for s in self.subjects.values() if s.code == "sport"]

        for task_idx, (class_id, subject_id, teacher_id, hours) in enumerate(tasks):
            c = next((x for x in self.classes if x.id == class_id), None)
            if not c:
                continue
            slots = get_slots_for_class(c)
            if not slots:
                continue
            num_slots = len(slots)
            vars_for_task = []
            for day in days:
                for slot_idx in range(num_slots):
                    var = model.NewBoolVar(f"task_{task_idx}_d{day}_s{slot_idx}")
                    task_vars[(task_idx, day, slot_idx)] = var
                    vars_for_task.append(var)
                    teacher_occ.setdefault((teacher_id, day, slot_idx), []).append(var)
                    class_occ.setdefault((class_id, day, slot_idx), []).append(var)
            # 每个任务必须被安排 hours 次
            model.Add(sum(vars_for_task) == hours)

            # 软约束: 主科优先上午 (slot_idx < slots/2)
            subject = self.subjects.get(subject_id)
            if subject and subject.is_main:
                morning_count = sum(
                    task_vars[(task_idx, day, slot_idx)]
                    for day in days for slot_idx in range(num_slots)
                    if slot_idx < num_slots / 2
                )
                # 体育优先下午
            if subject and subject.code == "sport":
                afternoon_count = sum(
                    task_vars[(task_idx, day, slot_idx)]
                    for day in days for slot_idx in range(num_slots)
                    if slot_idx >= num_slots / 2
                )

        # 硬约束: 教师/班级/教室 同一时间唯一
        for key, vars_list in teacher_occ.items():
            if len(vars_list) > 1:
                model.Add(sum(vars_list) <= 1)
        for key, vars_list in class_occ.items():
            if len(vars_list) > 1:
                model.Add(sum(vars_list) <= 1)

        # 软约束加权: 主科上午、体育下午、课程分散等
        objective_terms = []
        for task_idx, (class_id, subject_id, teacher_id, hours) in enumerate(tasks):
            c = next((x for x in self.classes if x.id == class_id), None)
            if not c:
                continue
            slots = get_slots_for_class(c)
            num_slots = len(slots)
            subject = self.subjects.get(subject_id)
            for day in days:
                for slot_idx in range(num_slots):
                    key = (task_idx, day, slot_idx)
                    if key in task_vars:
                        var = task_vars[key]
                        if subject and subject.is_main and slot_idx < num_slots / 2:
                            objective_terms.append(var * 3)
                        if subject and subject.code == "sport" and slot_idx >= num_slots / 2:
                            objective_terms.append(var * 2)
                        # 避免最后一节主科
                        if subject and subject.is_main and slot_idx == num_slots - 1:
                            objective_terms.append(var * -1)

        if objective_terms:
            model.Maximize(sum(objective_terms))

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 120
        solver.parameters.num_workers = 4
        status = solver.Solve(model)

        entries = []
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            logger.info(f"排课成功: status={status}, obj={solver.ObjectiveValue()}")
            for task_idx, (class_id, subject_id, teacher_id, hours) in enumerate(tasks):
                c = next((x for x in self.classes if x.id == class_id), None)
                if not c:
                    continue
                slots = get_slots_for_class(c)
                plan_id = c.schedule_plan_id or 1
                cycle_all = next((c.id for c in self.cycles if c.code == "ALL"), 1)
                for day in days:
                    for slot_idx in range(len(slots)):
                        key = (task_idx, day, slot_idx)
                        if key in task_vars and solver.Value(task_vars[key]) == 1:
                            slot = slots[slot_idx]
                            # 选择教室
                            subject = self.subjects.get(subject_id)
                            room_id = None
                            if subject and subject.need_room:
                                for rid, room in self.classrooms.items():
                                    if room.subject_ids and subject_id in room.subject_ids:
                                        room_id = rid
                                        break
                            entries.append({
                                "class_id": class_id,
                                "subject_id": subject_id,
                                "teacher_id": teacher_id,
                                "classroom_id": room_id,
                                "day_of_week": day,
                                "time_slot_id": slot.id,
                                "schedule_plan_id": plan_id,
                                "cycle_id": cycle_all,
                                "is_fixed": False,
                            })
            return status, entries
        else:
            logger.error(f"排课失败: status={status}")
            return status, []

    def save_entries(self, entries: List[dict]) -> int:
        # 清理旧 entries
        self.db.query(TimetableEntry).filter(TimetableEntry.version_id == self.version_id).delete()
        for e in entries:
            inst = TimetableEntry(
                version_id=self.version_id,
                academic_year_id=self.academic_year_id,
                semester_id=self.semester_id,
                **e
            )
            self.db.add(inst)
        self.db.commit()
        return len(entries)
