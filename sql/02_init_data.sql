-- 初始化数据脚本
-- 执行顺序: 01_schema.sql -> 02_init_data.sql

USE school_scheduling;

-- 角色
INSERT INTO `sys_role` (`role_code`, `role_name`, `description`) VALUES
('admin', '系统管理员', '拥有全部权限'),
('academic', '教务管理员', '管理教务数据与排课'),
('teacher', '教师', '查看课表与发起换课'),
('leader', '校领导', '查看统计报表');

-- 权限点
INSERT INTO `sys_permission` (`perm_code`, `perm_name`, `module`) VALUES
('basic:teacher:manage', '教师管理', 'basic'),
('basic:class:manage', '班级管理', 'basic'),
('basic:classroom:manage', '教室管理', 'basic'),
('basic:subject:manage', '科目管理', 'basic'),
('hr:manage', '人事表管理', 'hr'),
('schedule:auto', '自动排课', 'scheduling'),
('schedule:manual', '手动调课', 'scheduling'),
('swap:approve', '换课审批', 'scheduling'),
('year:manage', '学年管理', 'basic'),
('stats:view', '查看统计', 'stats'),
('timetable:view', '查看课表', 'timetable'),
('swap:request', '发起换课', 'swap'),
('notification:manage', '通知管理', 'notification');

-- 角色权限分配
INSERT INTO `sys_role_permission` (`role_code`, `perm_code`) VALUES
('admin', 'basic:teacher:manage'),
('admin', 'basic:class:manage'),
('admin', 'basic:classroom:manage'),
('admin', 'basic:subject:manage'),
('admin', 'hr:manage'),
('admin', 'schedule:auto'),
('admin', 'schedule:manual'),
('admin', 'swap:approve'),
('admin', 'year:manage'),
('admin', 'stats:view'),
('admin', 'timetable:view'),
('admin', 'notification:manage'),
('academic', 'basic:teacher:manage'),
('academic', 'basic:class:manage'),
('academic', 'basic:classroom:manage'),
('academic', 'basic:subject:manage'),
('academic', 'hr:manage'),
('academic', 'schedule:auto'),
('academic', 'schedule:manual'),
('academic', 'swap:approve'),
('academic', 'stats:view'),
('academic', 'timetable:view'),
('teacher', 'timetable:view'),
('teacher', 'swap:request'),
('leader', 'timetable:view'),
('leader', 'stats:view');

-- 年级
INSERT INTO `grade` (`name`, `level`) VALUES
('一年级', 1),
('二年级', 2),
('三年级', 3),
('四年级', 4),
('五年级', 5),
('六年级', 6);

-- 科目
INSERT INTO `subject` (`name`, `code`, `is_main`, `need_room`, `color`, `sort_order`) VALUES
('语文', 'chinese', 1, 0, '#E74C3C', 1),
('数学', 'math', 1, 0, '#3498DB', 2),
('英语', 'english', 1, 0, '#27AE60', 3),
('道法', 'daofa', 0, 0, '#8E44AD', 4),
('科学', 'science', 0, 1, '#16A085', 5),
('信息科技', 'it', 0, 1, '#2C3E50', 6),
('音乐', 'music', 0, 1, '#E67E22', 7),
('体育', 'sport', 0, 1, '#F39C12', 8),
('美术', 'art', 0, 1, '#D35400', 9),
('劳动', 'labor', 0, 0, '#7F8C8D', 10),
('心理', 'psychology', 0, 0, '#9B59B6', 11),
('健康', 'health', 0, 0, '#1ABC9C', 12),
('综合实践', 'practice', 0, 0, '#34495E', 13),
('校本课程', 'schoolbased', 0, 0, '#C0392B', 14),
('阅读课', 'reading', 0, 0, '#2980B9', 15),
('自习课', 'selfstudy', 0, 0, '#95A5A6', 16);

-- 课程周期
INSERT INTO `course_cycle` (`code`, `name`, `week_mask`) VALUES
('ALL', '每周', '11111111111111111111'),
('ODD', '单周', '10101010101010101010'),
('EVEN', '双周', '01010101010101010101'),
('A', 'A周', '11111111110000000000'),
('B', 'B周', '00000000001111111111'),
('C', 'C周', '10001000100010001000');

-- 作息方案 - 低年级
INSERT INTO `schedule_plan` (`name`, `description`, `is_default`) VALUES
('低年级作息', '一、二年级作息时间', 1);

-- 低年级时间段
INSERT INTO `time_slot` (`schedule_plan_id`, `period_no`, `period_name`, `start_time`, `end_time`, `is_break`, `sort_order`) VALUES
(1, 1, '第一节', '08:00', '08:35', 0, 1),
(1, 2, '第二节', '08:45', '09:20', 0, 2),
(1, 0, '课间操', '09:20', '09:40', 1, 3),
(1, 3, '第三节', '09:40', '10:15', 0, 4),
(1, 4, '第四节', '10:25', '11:00', 0, 5),
(1, 0, '午休', '11:00', '14:00', 1, 6),
(1, 5, '第五节', '14:00', '14:35', 0, 7),
(1, 6, '第六节', '14:45', '15:20', 0, 8),
(1, 7, '第七节', '15:30', '16:05', 0, 9);

-- 作息方案 - 中高年级
INSERT INTO `schedule_plan` (`name`, `description`, `is_default`) VALUES
('中高年级作息', '三至六年级作息时间', 0);

INSERT INTO `time_slot` (`schedule_plan_id`, `period_no`, `period_name`, `start_time`, `end_time`, `is_break`, `sort_order`) VALUES
(2, 1, '第一节', '08:00', '08:40', 0, 1),
(2, 2, '第二节', '08:50', '09:30', 0, 2),
(2, 0, '课间操', '09:30', '09:50', 1, 3),
(2, 3, '第三节', '09:50', '10:30', 0, 4),
(2, 4, '第四节', '10:40', '11:20', 0, 5),
(2, 0, '午休', '11:20', '14:00', 1, 6),
(2, 5, '第五节', '14:00', '14:40', 0, 7),
(2, 6, '第六节', '14:50', '15:30', 0, 8),
(2, 7, '第七节', '15:40', '16:20', 0, 9);

-- 默认管理员账号 admin/123456 (bcrypt hash)
INSERT INTO `sys_user` (`username`, `password_hash`, `real_name`, `role_code`, `first_login`, `status`) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lewy5KsT.0v02yGjK', '系统管理员', 'admin', 0, 1),
('academic01', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lewy5KsT.0v02yGjK', '张教务', 'academic', 0, 1);

-- 示例教师
INSERT INTO `teacher` (`teacher_no`, `name`, `gender`, `title`, `main_subject_id`, `subject_ids`, `max_weekly_hours`, `max_daily_hours`) VALUES
('T2024001', '张老师', 'female', '小学高级教师', 1, '[1, 15]', 20, 4),
('T2024002', '李老师', 'female', '小学高级教师', 2, '[2]', 20, 4),
('T2024003', '王老师', 'male', '小学一级教师', 3, '[3]', 20, 4),
('T2024004', '赵老师', 'female', '小学一级教师', 8, '[8]', 16, 3),
('T2024005', '钱老师', 'male', '小学高级教师', 7, '[7]', 16, 3),
('T2024006', '孙老师', 'female', '小学一级教师', 9, '[9]', 16, 3),
('T2024007', '周老师', 'male', '小学一级教师', 5, '[5, 6]', 16, 3),
('T2024008', '吴老师', 'female', '小学高级教师', 4, '[4, 11, 12]', 16, 3);

-- 教师账号
INSERT INTO `sys_user` (`username`, `password_hash`, `real_name`, `role_code`, `teacher_id`, `first_login`, `status`) VALUES
('T2024001', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lewy5KsT.0v02yGjK', '张老师', 'teacher', 1, 1, 1),
('T2024002', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lewy5KsT.0v02yGjK', '李老师', 'teacher', 2, 1, 1),
('T2024003', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lewy5KsT.0v02yGjK', '王老师', 'teacher', 3, 1, 1);

-- 示例教室
INSERT INTO `classroom` (`name`, `type`, `capacity`, `subject_ids`, `location`) VALUES
('一(1)班教室', 'normal', 45, NULL, '教学楼1-101'),
('一(2)班教室', 'normal', 45, NULL, '教学楼1-102'),
('二(1)班教室', 'normal', 45, NULL, '教学楼1-201'),
('三(1)班教室', 'normal', 45, NULL, '教学楼2-101'),
('四(1)班教室', 'normal', 45, NULL, '教学楼2-201'),
('五(1)班教室', 'normal', 45, NULL, '教学楼3-101'),
('六(1)班教室', 'normal', 45, NULL, '教学楼3-201'),
('微机室1', 'computer', 48, '[6]', '综合楼4-401'),
('科学实验室', 'lab', 45, '[5]', '综合楼3-301'),
('音乐教室1', 'music', 45, '[7]', '综合楼2-201'),
('美术教室', 'art', 45, '[9]', '综合楼2-202'),
('录播教室', 'recording', 40, NULL, '综合楼1-101'),
('操场', 'sport', 200, '[8]', '操场');

-- 示例学年学期
INSERT INTO `academic_year` (`name`, `start_date`, `end_date`, `is_archived`, `is_current`) VALUES
('2024-2025', '2024-09-01', '2025-07-15', 0, 1);

INSERT INTO `semester` (`academic_year_id`, `name`, `start_date`, `end_date`, `total_weeks`, `is_current`) VALUES
(1, '第一学期', '2024-09-01', '2025-01-20', 20, 1),
(1, '第二学期', '2025-02-20', '2025-07-15', 20, 0);

-- 示例班级
INSERT INTO `class_info` (`name`, `grade_id`, `student_count`, `schedule_plan_id`, `academic_year_id`) VALUES
('一(1)班', 1, 42, 1, 1),
('一(2)班', 1, 40, 1, 1),
('二(1)班', 2, 43, 1, 1),
('三(1)班', 3, 45, 2, 1),
('四(1)班', 4, 44, 2, 1),
('五(1)班', 5, 42, 2, 1),
('六(1)班', 6, 40, 2, 1);
