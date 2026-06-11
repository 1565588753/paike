# 智慧教务与智能排课管理平台 (School Smart Scheduling System)

面向小学的一体化教务与智能排课系统，集教师人事、学年学期、多作息方案、自动排课（Google OR-Tools 约束求解）、手动调课、教师自主换课、课表导出与教务统计分析于一体。

- **技术栈**: Python 3.11 / FastAPI / SQLAlchemy / MySQL 8 / Redis 7 / OR-Tools
- **前端**: Vue 3 + TypeScript + Vite + Element Plus + Pinia + ECharts
- **部署**: Docker Compose（backend / frontend / mysql / redis）

---

## 1. 快速启动

```bash
# 克隆或解压项目后, 在项目根目录:
docker compose up -d --build

# 初始化数据库（等待 MySQL 就绪后）
docker exec school-backend python scripts/init_db.py

# 浏览器访问
# 前端: http://localhost:5173
# 后端 API: http://localhost:8000/docs

# 默认账号
# 管理员: admin / 123456
# 教务管理员账号由管理员创建
# 教师账号: 工号 / 123456（首次登录强制改密）
```

---

## 2. 目录结构

```
.
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── main.py             # 应用入口 / 路由装配
│   │   ├── api/v1/endpoints/   # 认证 / 教师 / 班级 / 科目 / 学年 / HR / 课表 / 换课 / 统计
│   │   ├── core/               # 数据库 / JWT 安全 / 配置 / 日志
│   │   ├── models/             # SQLAlchemy ORM 模型
│   │   ├── schemas/            # Pydantic 请求/响应
│   │   ├── services/           # 排课引擎 / 冲突检测 / 质量评分 / 导出服务 / 数据仓库
│   │   └── tests/              # pytest 单元测试
│   ├── scripts/                # init_db / upgrade_year / export_timetable
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Vue 3 + TS + Element Plus
│   ├── src/
│   │   ├── layouts/            # 主体布局
│   │   ├── views/              # 业务页面（auth / dashboard / basic / hr / timetable / stats）
│   │   ├── stores/             # Pinia: auth + app
│   │   ├── router/             # 路由与权限守卫
│   │   └── utils/request.ts    # axios 实例 / JWT 注入 / 401 重登录
│   ├── nginx.conf
│   ├── Dockerfile
│   └── vite.config.ts
├── sql/
│   ├── 01_schema.sql           # 完整建表脚本（20+ 张表）
│   └── 02_init_data.sql        # 角色 / 年级 / 科目 / 作息 / 示例班级
├── docker-compose.yml          # 一键编排 backend / frontend / mysql / redis
└── README.md
```

---

## 3. 角色与权限

| 角色 | 能力 |
|------|------|
| `admin` 系统管理员 | 全权限 |
| `academic` 教务管理员 | 教师/班级/教室/科目/人事/自动排课/手动调课/换课审批/学年管理/统计 |
| `teacher` 教师 | 查看课表 / 发起换课 / 确认换课 |
| `leader` 校领导 | 查看课表 / 统计分析 / 教师工作量 |

---

## 4. 核心功能速览

### 4.1 智能排课引擎（OR-Tools CP-SAT）
- **硬约束**: 教师冲突、班级冲突、教室冲突、课时不足、固定课冲突、禁排时间、单双周、时间区间重叠、专用教室冲突
- **软约束**: 语数外优先上午、体育优先下午、课程均衡、教师均衡、避免主科最后一节、连堂课合理、课程分散
- 接口: `POST /api/v1/timetable/versions/{id}/auto-schedule`
- 质量评分: 主科覆盖率、教师均衡度、课程均衡度、教室利用率、连堂课合理性 → 汇总总分

### 4.2 时间区间冲突检测
- 禁止仅凭"星期+节次"判断，改用实际起止时间（start_time / end_time）区间重叠算法，天然兼容多作息方案合并班级。

### 4.3 多作息方案
- 低年级作息、中高年级作息可任意配置时段，班级绑定任意作息方案。

### 4.4 人事表
- 班主任 / 各科目教师录入、Excel 导入导出、学年升级继承、周课时配置。

### 4.5 课程周期（单双周 / A周B周）
- 周一第七节: 单周心理 / 双周健康 → 由 `course_cycle` 表 week_mask 控制，排课时可按 `cycle_id` 区分。

### 4.6 学年管理与升级
- 学年归档、当前学年切换、一键升级（自动生成新班级与新一年级）。

### 4.7 教师自主换课
- 发起 → 对方确认 → 审批（可选）→ 生效；流程与消息通知中心打通。

### 4.8 课表导出
- Excel / PDF / Word 预览打印；可选是否显示教师姓名。

---

## 5. 主要 API 端点

所有接口统一前缀 `/api/v1`。详情通过 Swagger UI `http://localhost:8000/docs` 查看。

| 模块 | 方法 | 路径 |
|------|------|------|
| 认证 | POST | `/auth/login` |
| 认证 | POST | `/auth/change-password` |
| 教师 | GET/POST/PUT/DELETE | `/teachers` |
| 基础 | GET/POST | `/classes`, `/subjects`, `/classrooms`, `/grades` |
| 学年 | GET/POST/PUT | `/years`, `/years/{id}/semesters`, `/years/{id}/archive`, `/years/{id}/upgrade` |
| 作息 | GET/POST | `/schedule-plans`, `/cycles` |
| 人事 | GET/POST | `/hr-records`, `/weekly-hours` |
| 课表 | GET/POST/PUT/DELETE | `/timetable/versions`, `/timetable/versions/{id}/auto-schedule`, `/timetable/versions/{id}/publish` |
| 课表条目 | GET/POST/PUT/DELETE | `/timetable/entries`, `/timetable/entries/{id}/move`, `/timetable/entries/swap` |
| 换课 | GET/POST | `/swaps`, `/swaps/{id}/confirm`, `/swaps/{id}/reject`, `/swaps/{id}/approve` |
| 统计 | GET | `/stats/teacher-workload`, `/stats/subject-distribution`, `/stats/classroom-utilization` |
| 消息 | GET | `/notifications` |
| 系统 | GET | `/health`, `/info` |

---

## 6. 数据库 ER 概览

核心实体与关系:

```
sys_user ──(role_code)──▶ sys_role ──▶ sys_role_permission ◀── sys_permission
 │
 └─ teacher_id ──▶ teacher ── (subject_ids, forbid_slots JSON)
                     │
                     ▼
           hr_record (academic_year, semester, class, subject_teachers JSON)
                     │
                     ▼
           class_info ──▶ academic_year / semester / schedule_plan / grade
                     │
                     ▼
           timetable_entry ──▶ timetable_version (draft/published)
                                ├─ subject / teacher / classroom / time_slot
                                └─ course_cycle (ALL / ODD / EVEN / A / B / C)
           swap_request ──▶ entry_a / entry_b
           adjustment_record
           special_date, notification, sys_operation_log, subject_weekly_plan,
           timetable_quality
```

详细字段定义见 `sql/01_schema.sql`。

---

## 7. 命令行工具

```bash
# 初始化数据库（首次部署）
docker exec school-backend python scripts/init_db.py

# 学年升级
docker exec school-backend python scripts/upgrade_year.py \
    --from-year-id 1 \
    --to-year-name 2025-2026 \
    --to-year-start 2025-09-01 \
    --to-year-end 2026-07-15

# 课表导出（按版本 / 班级）
docker exec school-backend python scripts/export_timetable.py --version 1 --class-id 1

# 运行单元测试
docker exec school-backend python -m pytest app/tests -v
```

---

## 8. 质量与可维护性

- 所有 API 返回统一 `{ code, message, data }` 格式
- 全局 HTTP 异常与参数校验错误拦截
- `sys_operation_log` 记录关键操作
- 课表质量评分自动生成并与版本绑定
- 前端使用 ECharts 可视化: 教师负载、科目分布、教室利用率、每日课节

---

## 9. 安全

- JWT Bearer Token（24 小时有效期，可通过 `JWT_EXPIRE_MINUTES` 调整）
- 密码使用 `passlib[bcrypt]` 哈希存储
- 首次登录强制修改密码
- 前端路由基于角色守卫，后端接口基于角色装饰器 `RoleRequired`

---

## 10. 常见问题

**Q: 启动时数据库尚未就绪?**
A: `init_db.py` 内置重试，后端服务也在 `depends_on -> condition: service_healthy` 下等待 MySQL 健康检查通过再启动。

**Q: 如何新增科目?**
A: 教务管理员 → 基础数据 → 科目管理 → 新增。

**Q: 如何执行首次自动排课?**
A: 学年 / 学期 / 班级 / 人事 / 周课时配置完毕后 → 课表编辑 → 新建版本 → 自动排课。

**Q: OR-Tools 排不出?**
A: 常见原因: 周课时总量超过教师最大周课时 / 每日课时 / 时段数量。可通过提高教师数量、降低周课时、增加时段解决。

---

© 2025 School Smart Scheduling System
