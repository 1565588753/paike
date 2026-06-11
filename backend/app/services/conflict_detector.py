from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Tuple
from app.models.scheduling import TimetableEntry, TimeSlot, CourseCycle


class ConflictDetector:
    """时间区间冲突检测 - 基于实际时间段 start/end 检测。"""

    def __init__(self, db: Session):
        self.db = db

    def _load_slot(self, slot_id: int) -> Optional[TimeSlot]:
        return self.db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()

    def _overlaps(self, s1_start: str, s1_end: str, s2_start: str, s2_end: str) -> bool:
        # 将 "HH:MM" 转换为分钟数以比较
        def to_min(s):
            h, m = s.split(":")
            return int(h) * 60 + int(m)
        s1s, s1e, s2s, s2e = to_min(s1_start), to_min(s1_end), to_min(s2_start), to_min(s2_end)
        return s1s < s2e and s2s < s1e

    def check_conflict(self, version_id: int, class_id: int = None, teacher_id: int = None,
                       classroom_id: int = None, day_of_week: int = None,
                       time_slot_id: int = None, exclude_entry_id: int = None,
                       cycle_id: int = None) -> List[dict]:
        """检查指定 (班级/教师/教室 + 星期 + 时间段) 是否存在冲突。返回冲突列表。"""
        conflicts = []
        # 加载被检测的时间段
        slot = self._load_slot(time_slot_id)
        if not slot:
            return conflicts

        # 加载所有同版本的条目
        entries = self.db.query(TimetableEntry).filter(TimetableEntry.version_id == version_id).all()
        if exclude_entry_id:
            entries = [e for e in entries if e.id != exclude_entry_id]

        # 加载所有时间段
        all_slots = {s.id: s for s in self.db.query(TimeSlot).all()}

        for e in entries:
            if e.day_of_week != day_of_week:
                continue
            e_slot = all_slots.get(e.time_slot_id)
            if not e_slot:
                continue
            if not self._overlaps(slot.start_time, slot.end_time, e_slot.start_time, e_slot.end_time):
                continue
            # 周期冲突: 两个条目周次掩码必须有重叠
            if cycle_id and e.cycle_id != cycle_id:
                cycle_a = self.db.query(CourseCycle).filter(CourseCycle.id == cycle_id).first()
                cycle_b = self.db.query(CourseCycle).filter(CourseCycle.id == e.cycle_id).first()
                if cycle_a and cycle_b:
                    has_overlap = any(a == '1' and b == '1' for a, b in zip(cycle_a.week_mask, cycle_b.week_mask))
                    if not has_overlap:
                        continue
            if class_id and e.class_id == class_id:
                conflicts.append({"type": "class", "entry_id": e.id, "reason": "班级时间冲突"})
            if teacher_id and e.teacher_id == teacher_id:
                conflicts.append({"type": "teacher", "entry_id": e.id, "reason": "教师时间冲突"})
            if classroom_id and e.classroom_id == classroom_id and classroom_id:
                conflicts.append({"type": "classroom", "entry_id": e.id, "reason": "教室时间冲突"})
        return conflicts
