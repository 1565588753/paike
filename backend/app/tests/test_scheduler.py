import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ortools.sat.python import cp_model


def test_simple_schedule():
    """测试 or-tools 求解简单的排课问题: 2个班级2个科目2个时段, 寻找可行解。"""
    model = cp_model.CpModel()
    classes = ["c1", "c2"]
    subjects = ["s1", "s2"]
    days = [1, 2]

    x = {}
    for c in classes:
        for s in subjects:
            for d in days:
                x[(c, s, d)] = model.NewBoolVar(f"x_{c}_{s}_{d}")

    # 每个(班级,科目)组合每周排1节课
    for c in classes:
        for s in subjects:
            model.Add(sum(x[(c, s, d)] for d in days) == 1)

    # 每个班级每天最多1节课
    for c in classes:
        for d in days:
            model.Add(sum(x[(c, s, d)] for s in subjects) <= 1)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE), f"求解失败 status={status}"

    scheduled = []
    for (c, s, d), var in x.items():
        if solver.Value(var):
            scheduled.append((c, s, d))
    assert len(scheduled) == len(classes) * len(subjects)
    print("排课测试通过:", scheduled)


if __name__ == "__main__":
    test_simple_schedule()
    print("所有 OR-Tools 测试通过")
