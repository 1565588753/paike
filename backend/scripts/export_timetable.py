#!/usr/bin/env python3
"""课表导出工具: 按班级/教师导出 Excel/CSV。"""
import sys
import os
import csv
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openpyxl import Workbook
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.scheduling import TimetableEntry, ClassInfo, Teacher, Subject, Classroom, TimeSlot, TimetableVersion
from app.core.config import settings

DB_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"


def export_class_timetable(db, version_id, class_id, output_file=None):
    version = db.query(TimetableVersion).filter(TimetableVersion.id == version_id).first()
    cls = db.query(ClassInfo).filter(ClassInfo.id == class_id).first()
    slots = db.query(TimeSlot).filter(TimeSlot.schedule_plan_id == cls.schedule_plan_id).order_by(TimeSlot.sort_order).all()

    entries = db.query(TimetableEntry).filter(
        TimetableEntry.version_id == version_id,
        TimetableEntry.class_id == class_id
    ).all()

    subjects = {s.id: s for s in db.query(Subject).all()}
    teachers = {t.id: t for t in db.query(Teacher).all()}

    output_file = output_file or f"class_{class_id}_timetable_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "课表"
    ws.cell(row=1, column=1, value=f"{cls.name} 课表").font = ws.cell(row=1, column=1).font
    ws.cell(row=2, column=1, value=f"版本: {version.version_no}  ({version.version_name})")
    ws.append([])
    ws.append(["节次", "时间", "周一", "周二", "周三", "周四", "周五"])

    for slot in slots:
        row = [f"第{slot.period_no}节" if slot.period_no else slot.period_name,
               f"{slot.start_time}-{slot.end_time}"]
        for day in range(1, 6):
            cell = ""
            for e in entries:
                if e.day_of_week == day and e.time_slot_id == slot.id:
                    subj = subjects.get(e.subject_id)
                    teacher = teachers.get(e.teacher_id)
                    cell += f"{subj.name if subj else ''}"
                    if teacher:
                        cell += f"({teacher.name})"
                    cell += "\n"
            row.append(cell.strip())
        ws.append(row)

    wb.save(output_file)
    print(f"已导出: {output_file}")
    return output_file


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", type=int, required=True)
    parser.add_argument("--class-id", type=int, help="班级ID")
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    if args.class_id:
        export_class_timetable(db, args.version, args.class_id, args.output)
    else:
        # 导出所有班级
        classes = db.query(ClassInfo).all()
        for c in classes:
            try:
                export_class_timetable(db, args.version, c.id)
            except Exception as e:
                print(f"  班级 {c.name} 导出失败: {e}")
    db.close()


if __name__ == "__main__":
    main()
