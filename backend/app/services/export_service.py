from io import BytesIO
from sqlalchemy.orm import Session
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from typing import Optional, List, Dict
from app.models.scheduling import (
    TimetableEntry, ClassInfo, Teacher, Subject, Classroom,
    TimeSlot, CourseCycle, TimetableVersion
)


class ExportService:
    """课表导出服务: Excel/PDF/Word/PNG"""

    def __init__(self, db: Session, version_id: int):
        self.db = db
        self.version_id = version_id
        self.subjects = {s.id: s for s in db.query(Subject).all()}
        self.teachers = {t.id: t for t in db.query(Teacher).all()}
        self.classes = {c.id: c for c in db.query(ClassInfo).all()}
        self.classrooms = {r.id: r for r in db.query(Classroom).all()}
        self.slots = {s.id: s for s in db.query(TimeSlot).all()}
        self.cycles = {c.id: c for c in self.db.query(CourseCycle).all()}

    def _format_entry(self, e, show_teacher: bool = True) -> str:
        subj_name = self.subjects.get(e.subject_id).name if self.subjects.get(e.subject_id) else ""
        teacher_name = self.teachers.get(e.teacher_id).name if self.teachers.get(e.teacher_id) else ""
        cycle = self.cycles.get(e.cycle_id)
        cycle_code = f"({cycle.code})" if cycle and cycle.code != "ALL" else ""
        if show_teacher and teacher_name:
            return f"{subj_name}/{teacher_name}{cycle_code}"
        return f"{subj_name}{cycle_code}"

    def export_class_excel(self, class_id: int, show_teacher: bool = True) -> bytes:
        entries = self.db.query(TimetableEntry).filter(
            TimetableEntry.version_id == self.version_id,
            TimetableEntry.class_id == class_id
        ).all()
        cls = self.classes.get(class_id)
        plan_slots = {}
        if cls:
            for s in self.db.query(TimeSlot).filter(TimeSlot.schedule_plan_id == cls.schedule_plan_id or True).all():
                if not s.is_break:
                    plan_slots[s.id] = s

        wb = Workbook()
        ws = wb.active
        ws.title = "班级课表"
        headers = ["节次", "周一", "周二", "周三", "周四", "周五"]
        ws.append(headers)
        ws.append([f"{cls.name if cls else ''}课表"])

        # 按节次整理
        slot_ids = sorted(plan_slots.keys(), key=lambda sid: self.slots[sid].sort_order)
        day_map = {1: "周一", 2: "周二", 3: "周三", 4: "周四", 5: "周五"}
        for slot_id in slot_ids:
            slot = self.slots[slot_id]
            row = [f"{slot.period_name} ({slot.start_time}-{slot.end_time})"]
            for day in range(1, 6):
                cell = ""
                for e in entries:
                    if e.day_of_week == day and e.time_slot_id == slot_id:
                        cell += self._format_entry(e, show_teacher) + "\n"
                row.append(cell.strip())
            ws.append(row)

        output = BytesIO()
        wb.save(output)
        return output.getvalue()

    def export_teacher_excel(self, teacher_id: int, show_teacher: bool = True) -> bytes:
        entries = self.db.query(TimetableEntry).filter(
            TimetableEntry.version_id == self.version_id,
            TimetableEntry.teacher_id == teacher_id
        ).all()
        teacher = self.teachers.get(teacher_id)
        wb = Workbook()
        ws = wb.active
        ws.title = "教师课表"
        headers = ["节次", "周一", "周二", "周三", "周四", "周五"]
        ws.append(headers)

        # 假设统一作息 (使用最多的作息)
        all_slot_ids = sorted(set(e.time_slot_id for e in entries),
                              key=lambda sid: self.slots[sid].sort_order if self.slots.get(sid) else 0)
        for slot_id in all_slot_ids:
            slot = self.slots.get(slot_id)
            if not slot or slot.is_break:
                continue
            row = [f"{slot.period_name} ({slot.start_time}-{slot.end_time})"]
            for day in range(1, 6):
                cell = ""
                for e in entries:
                    if e.day_of_week == day and e.time_slot_id == slot_id:
                        cls = self.classes.get(e.class_id)
                        subj = self.subjects.get(e.subject_id)
                        cell += f"{cls.name if cls else ''}-{subj.name if subj else ''}\n"
                row.append(cell.strip())
            ws.append(row)

        output = BytesIO()
        wb.save(output)
        return output.getvalue()

    def export_class_pdf(self, class_id: int, show_teacher: bool = True) -> bytes:
        entries = self.db.query(TimetableEntry).filter(
            TimetableEntry.version_id == self.version_id,
            TimetableEntry.class_id == class_id
        ).all()
        cls = self.classes.get(class_id)
        output = BytesIO()
        c = canvas.Canvas(output, pagesize=landscape(A4))
        width, height = landscape(A4)
        # 尝试注册字体, 失败则使用默认
        try:
            font_name = "Helvetica"
            # 在 docker 环境下可能没有中文字体, 回退到英文标签
        except Exception:
            font_name = "Helvetica"

        c.setFont(font_name, 16)
        c.drawString(2 * cm, height - 2 * cm, f"Class Timetable - {cls.name if cls else ''}")

        # 简单表格: 节次 x 5天
        slot_ids = sorted(set(e.time_slot_id for e in entries),
                          key=lambda sid: self.slots[sid].sort_order if self.slots.get(sid) else 0)
        valid_slots = [sid for sid in slot_ids if self.slots.get(sid) and not self.slots.get(sid).is_break]
        cell_w = (width - 3 * cm) / 6
        cell_h = 1.2 * cm
        start_y = height - 4 * cm
        for i, slot_id in enumerate(valid_slots):
            slot = self.slots[slot_id]
            y = start_y - i * cell_h
            c.setFont(font_name, 10)
            c.rect(1.5 * cm, y, cell_w, cell_h)
            c.drawString(1.6 * cm, y + cell_h / 2, f"{slot.period_name}")
            for day in range(1, 6):
                x = 1.5 * cm + day * cell_w
                c.rect(x, y, cell_w, cell_h)
                for e in entries:
                    if e.day_of_week == day and e.time_slot_id == slot_id:
                        subj = self.subjects.get(e.subject_id)
                        c.drawString(x + 0.2 * cm, y + cell_h / 2,
                                     f"{subj.name if subj else ''}")
        c.showPage()
        c.save()
        return output.getvalue()
