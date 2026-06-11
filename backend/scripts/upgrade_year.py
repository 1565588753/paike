#!/usr/bin/env python3
"""学年升级工具: 将现有班级升级到下一学年, 创建新一年级。
Usage:
    python upgrade_year.py --from-year-id 1 --to-year-name 2025-2026 --to-year-start 2025-09-01 --to-year-end 2026-07-15
"""
import sys
import os
import argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.scheduling import AcademicYear, ClassInfo, Grade
from app.core.config import settings

DB_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-year-id", type=int, required=True, help="源学年ID")
    parser.add_argument("--to-year-name", type=str, required=True, help="新学年名称, 例如 2025-2026")
    parser.add_argument("--to-year-start", type=str, required=True, help="新学年起始日期")
    parser.add_argument("--to-year-end", type=str, required=True, help="新学年结束日期")
    args = parser.parse_args()

    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    source_year = db.query(AcademicYear).filter(AcademicYear.id == args.from_year_id).first()
    if not source_year:
        print(f"源学年 {args.from_year_id} 不存在")
        sys.exit(1)

    new_year = AcademicYear(
        name=args.to_year_name, start_date=args.to_year_start,
        end_date=args.to_year_end, is_current=True, is_archived=False
    )
    db.add(new_year)
    db.flush()

    grades = {g.level: g.id for g in db.query(Grade).all()}
    classes = db.query(ClassInfo).filter(ClassInfo.academic_year_id == args.from_year_id).all()

    upgraded = 0
    for c in classes:
        current_level = next((k for k, v in grades.items() if v == c.grade_id), None)
        if current_level is None or current_level >= 6:
            continue  # 六年级毕业
        new_level = current_level + 1
        nc = ClassInfo(
            name=f"{new_level}年级({c.name.split('(')[-1].rstrip('班') or str(upgraded + 1)})班",
            grade_id=grades[new_level],
            student_count=c.student_count,
            schedule_plan_id=c.schedule_plan_id,
            academic_year_id=new_year.id,
            status=1
        )
        db.add(nc)
        upgraded += 1

    # 创建新一年级 (示例)
    if 1 in grades:
        for i in range(1, 3):
            nc = ClassInfo(name=f"一({i})班", grade_id=grades[1], student_count=40,
                           academic_year_id=new_year.id, status=1)
            db.add(nc)

    # 归档旧学年
    source_year.is_archived = True
    source_year.is_current = False

    db.commit()
    print(f"新学年 {new_year.name} 创建成功, id={new_year.id}")
    print(f"升级班级: {upgraded} 个, 新一年级: 2 个")
    db.close()


if __name__ == "__main__":
    main()
