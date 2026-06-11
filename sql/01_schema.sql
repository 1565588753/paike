-- =====================================================
-- 智慧教务与智能排课管理平台 - 数据库建表脚本
-- Database: MySQL 8.0+
-- 字符集: utf8mb4
-- =====================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------
-- 用户与权限
-- -----------------------------------------------------

DROP TABLE IF EXISTS `sys_user`;
CREATE TABLE `sys_user` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(64) NOT NULL COMMENT '登录账号（工号）',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
    `real_name` VARCHAR(64) NOT NULL COMMENT '真实姓名',
    `avatar` VARCHAR(255) DEFAULT NULL,
    `phone` VARCHAR(32) DEFAULT NULL,
    `email` VARCHAR(128) DEFAULT NULL,
    `role_code` VARCHAR(32) NOT NULL DEFAULT 'teacher' COMMENT 'admin/academic/teacher/leader',
    `teacher_id` BIGINT DEFAULT NULL COMMENT '关联教师ID',
    `first_login` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '首次登录强制改密',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1启用 0禁用',
    `last_login_at` DATETIME DEFAULT NULL,
    `created_by` BIGINT DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    KEY `idx_teacher` (`teacher_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户账号表';

DROP TABLE IF EXISTS `sys_role`;
CREATE TABLE `sys_role` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `role_code` VARCHAR(32) NOT NULL,
    `role_name` VARCHAR(64) NOT NULL,
    `description` VARCHAR(255) DEFAULT NULL,
    `status` TINYINT NOT NULL DEFAULT 1,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_role_code` (`role_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';

DROP TABLE IF EXISTS `sys_permission`;
CREATE TABLE `sys_permission` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `perm_code` VARCHAR(128) NOT NULL,
    `perm_name` VARCHAR(128) NOT NULL,
    `module` VARCHAR(64) DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_perm_code` (`perm_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限点表';

DROP TABLE IF EXISTS `sys_role_permission`;
CREATE TABLE `sys_role_permission` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `role_code` VARCHAR(32) NOT NULL,
    `perm_code` VARCHAR(128) NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_role_perm` (`role_code`, `perm_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色-权限关联表';

-- -----------------------------------------------------
-- 学年学期
-- -----------------------------------------------------

DROP TABLE IF EXISTS `academic_year`;
CREATE TABLE `academic_year` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(32) NOT NULL COMMENT '例如 2024-2025',
    `start_date` DATE NOT NULL,
    `end_date` DATE NOT NULL,
    `is_archived` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否归档',
    `is_current` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否当前学年',
    `remark` VARCHAR(255) DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学年表';

DROP TABLE IF EXISTS `semester`;
CREATE TABLE `semester` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `academic_year_id` BIGINT NOT NULL,
    `name` VARCHAR(32) NOT NULL COMMENT '第一学期/第二学期',
    `start_date` DATE NOT NULL,
    `end_date` DATE NOT NULL,
    `total_weeks` INT NOT NULL DEFAULT 20,
    `is_current` TINYINT(1) NOT NULL DEFAULT 0,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_ay_sem` (`academic_year_id`, `name`),
    KEY `idx_ay` (`academic_year_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学期表';

-- -----------------------------------------------------
-- 基础数据
-- -----------------------------------------------------

DROP TABLE IF EXISTS `subject`;
CREATE TABLE `subject` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(32) NOT NULL COMMENT '科目名称',
    `code` VARCHAR(32) NOT NULL,
    `is_main` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否主科（语数外）',
    `need_room` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否需要专用教室',
    `color` VARCHAR(16) DEFAULT '#409EFF',
    `sort_order` INT NOT NULL DEFAULT 0,
    `status` TINYINT NOT NULL DEFAULT 1,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='科目表';

DROP TABLE IF EXISTS `teacher`;
CREATE TABLE `teacher` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `teacher_no` VARCHAR(32) NOT NULL COMMENT '工号',
    `name` VARCHAR(64) NOT NULL,
    `gender` VARCHAR(8) NOT NULL DEFAULT 'male',
    `phone` VARCHAR(32) DEFAULT NULL,
    `title` VARCHAR(64) DEFAULT NULL COMMENT '职称',
    `main_subject_id` BIGINT DEFAULT NULL COMMENT '所属学科',
    `subject_ids` JSON DEFAULT NULL COMMENT '可授课学科ID数组',
    `max_weekly_hours` INT NOT NULL DEFAULT 20,
    `max_daily_hours` INT NOT NULL DEFAULT 4,
    `forbid_slots` JSON DEFAULT NULL COMMENT '禁排时间',
    `status` TINYINT NOT NULL DEFAULT 1,
    `remark` VARCHAR(255) DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_teacher_no` (`teacher_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='教师表';

DROP TABLE IF EXISTS `grade`;
CREATE TABLE `grade` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(32) NOT NULL COMMENT '一年级/.../六年级',
    `level` INT NOT NULL COMMENT '1-6',
    `status` TINYINT NOT NULL DEFAULT 1,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_level` (`level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='年级表';

DROP TABLE IF EXISTS `class_info`;
CREATE TABLE `class_info` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(32) NOT NULL COMMENT '一(1)班',
    `grade_id` BIGINT NOT NULL,
    `student_count` INT NOT NULL DEFAULT 40,
    `schedule_plan_id` BIGINT DEFAULT NULL COMMENT '作息方案',
    `academic_year_id` BIGINT NOT NULL,
    `remark` VARCHAR(255) DEFAULT NULL,
    `status` TINYINT NOT NULL DEFAULT 1,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_grade` (`grade_id`),
    KEY `idx_ay` (`academic_year_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='班级表';

DROP TABLE IF EXISTS `classroom`;
CREATE TABLE `classroom` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(64) NOT NULL,
    `type` VARCHAR(32) NOT NULL DEFAULT 'normal' COMMENT 'normal/computer/lab/music/art/recording/sport/function',
    `capacity` INT NOT NULL DEFAULT 45,
    `subject_ids` JSON DEFAULT NULL COMMENT '专用教室适用科目',
    `location` VARCHAR(128) DEFAULT NULL,
    `status` TINYINT NOT NULL DEFAULT 1,
    `remark` VARCHAR(255) DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='教室表';

-- -----------------------------------------------------
-- 作息方案与时间段
-- -----------------------------------------------------

DROP TABLE IF EXISTS `schedule_plan`;
CREATE TABLE `schedule_plan` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(64) NOT NULL COMMENT '低年级/中高年级',
    `description` VARCHAR(255) DEFAULT NULL,
    `is_default` TINYINT(1) NOT NULL DEFAULT 0,
    `status` TINYINT NOT NULL DEFAULT 1,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='作息方案表';

DROP TABLE IF EXISTS `time_slot`;
CREATE TABLE `time_slot` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `schedule_plan_id` BIGINT NOT NULL,
    `period_no` INT NOT NULL COMMENT '第几节（1,2,3...）',
    `period_name` VARCHAR(32) NOT NULL COMMENT '第一节/课间操/午休',
    `start_time` TIME NOT NULL,
    `end_time` TIME NOT NULL,
    `is_break` TINYINT(1) NOT NULL DEFAULT 0,
    `sort_order` INT NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    KEY `idx_plan` (`schedule_plan_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='时间段表';

-- -----------------------------------------------------
-- 课程周期
-- -----------------------------------------------------

DROP TABLE IF EXISTS `course_cycle`;
CREATE TABLE `course_cycle` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `code` VARCHAR(32) NOT NULL COMMENT 'ALL/ODD/EVEN/A/B/C',
    `name` VARCHAR(64) NOT NULL,
    `week_mask` VARCHAR(32) NOT NULL DEFAULT '11111111111111111111' COMMENT '20周字符串 1=有课',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程周期表';

-- -----------------------------------------------------
-- 人事表
-- -----------------------------------------------------

DROP TABLE IF EXISTS `hr_record`;
CREATE TABLE `hr_record` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `academic_year_id` BIGINT NOT NULL,
    `semester_id` BIGINT NOT NULL,
    `class_id` BIGINT NOT NULL,
    `head_teacher_id` BIGINT DEFAULT NULL COMMENT '班主任',
    `subject_teachers` JSON NOT NULL COMMENT '{subject_id: teacher_id}',
    `remark` VARCHAR(255) DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_class_sem` (`class_id`, `semester_id`),
    KEY `idx_ay` (`academic_year_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='人事分配表';

-- -----------------------------------------------------
-- 课表（核心）
-- -----------------------------------------------------

DROP TABLE IF EXISTS `timetable_version`;
CREATE TABLE `timetable_version` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `academic_year_id` BIGINT NOT NULL,
    `semester_id` BIGINT NOT NULL,
    `version_no` VARCHAR(32) NOT NULL,
    `version_name` VARCHAR(128) DEFAULT NULL,
    `status` VARCHAR(16) NOT NULL DEFAULT 'draft' COMMENT 'draft/published/archived',
    `published_at` DATETIME DEFAULT NULL,
    `remark` VARCHAR(255) DEFAULT NULL,
    `quality_score` DECIMAL(5, 2) DEFAULT NULL,
    `created_by` BIGINT DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_ay_sem` (`academic_year_id`, `semester_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课表版本表';

DROP TABLE IF EXISTS `timetable_entry`;
CREATE TABLE `timetable_entry` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `version_id` BIGINT NOT NULL,
    `academic_year_id` BIGINT NOT NULL,
    `semester_id` BIGINT NOT NULL,
    `class_id` BIGINT NOT NULL,
    `subject_id` BIGINT NOT NULL,
    `teacher_id` BIGINT NOT NULL,
    `classroom_id` BIGINT DEFAULT NULL,
    `day_of_week` INT NOT NULL COMMENT '1-5 (周一到周五)',
    `time_slot_id` BIGINT NOT NULL,
    `schedule_plan_id` BIGINT NOT NULL,
    `cycle_id` BIGINT NOT NULL COMMENT '课程周期',
    `is_fixed` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '固定课不可动',
    `remark` VARCHAR(255) DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_version` (`version_id`),
    KEY `idx_class` (`class_id`),
    KEY `idx_teacher` (`teacher_id`),
    KEY `idx_day_slot` (`day_of_week`, `time_slot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课表条目表';

-- -----------------------------------------------------
-- 换课/调课
-- -----------------------------------------------------

DROP TABLE IF EXISTS `swap_request`;
CREATE TABLE `swap_request` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `version_id` BIGINT NOT NULL,
    `academic_year_id` BIGINT NOT NULL,
    `semester_id` BIGINT NOT NULL,
    `requester_teacher_id` BIGINT NOT NULL,
    `target_teacher_id` BIGINT NOT NULL,
    `entry_a_id` BIGINT NOT NULL COMMENT '发起方课表条目',
    `entry_b_id` BIGINT DEFAULT NULL COMMENT '对方课表条目（如对调）',
    `type` VARCHAR(16) NOT NULL DEFAULT 'swap' COMMENT 'swap/takeover',
    `reason` VARCHAR(500) DEFAULT NULL,
    `status` VARCHAR(16) NOT NULL DEFAULT 'pending' COMMENT 'pending/approved/rejected/cancelled',
    `requested_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `confirmed_at` DATETIME DEFAULT NULL,
    `approved_at` DATETIME DEFAULT NULL,
    `approved_by` BIGINT DEFAULT NULL,
    `effective_at` DATE DEFAULT NULL,
    `remark` VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_requester` (`requester_teacher_id`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='换课申请表';

DROP TABLE IF EXISTS `adjustment_record`;
CREATE TABLE `adjustment_record` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `version_id` BIGINT NOT NULL,
    `academic_year_id` BIGINT NOT NULL,
    `semester_id` BIGINT NOT NULL,
    `operator_id` BIGINT NOT NULL,
    `type` VARCHAR(16) NOT NULL COMMENT 'move/swap/batch/class',
    `detail` JSON DEFAULT NULL COMMENT '操作详情',
    `operator_note` VARCHAR(500) DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_version` (`version_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='调课记录表';

-- -----------------------------------------------------
-- 节假日/特殊日期
-- -----------------------------------------------------

DROP TABLE IF EXISTS `special_date`;
CREATE TABLE `special_date` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `academic_year_id` BIGINT NOT NULL,
    `semester_id` BIGINT DEFAULT NULL,
    `date` DATE NOT NULL,
    `type` VARCHAR(16) NOT NULL COMMENT 'holiday/event/exam/suspend',
    `name` VARCHAR(128) NOT NULL,
    `remark` VARCHAR(255) DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_date` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='节假日/特殊日期表';

-- -----------------------------------------------------
-- 通知消息
-- -----------------------------------------------------

DROP TABLE IF EXISTS `notification`;
CREATE TABLE `notification` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `recipient_user_id` BIGINT NOT NULL,
    `type` VARCHAR(32) NOT NULL COMMENT 'system/swap/approval/adjustment/announce',
    `title` VARCHAR(255) NOT NULL,
    `content` TEXT,
    `related_id` BIGINT DEFAULT NULL,
    `related_type` VARCHAR(32) DEFAULT NULL,
    `is_read` TINYINT(1) NOT NULL DEFAULT 0,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_recipient` (`recipient_user_id`),
    KEY `idx_read` (`is_read`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知消息表';

-- -----------------------------------------------------
-- 操作日志
-- -----------------------------------------------------

DROP TABLE IF EXISTS `sys_operation_log`;
CREATE TABLE `sys_operation_log` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT DEFAULT NULL,
    `username` VARCHAR(64) DEFAULT NULL,
    `operation` VARCHAR(128) NOT NULL,
    `module` VARCHAR(64) DEFAULT NULL,
    `method` VARCHAR(16) DEFAULT NULL,
    `params` TEXT,
    `ip_address` VARCHAR(64) DEFAULT NULL,
    `status` TINYINT DEFAULT 1,
    `error_msg` TEXT,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user` (`user_id`),
    KEY `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';

-- -----------------------------------------------------
-- 排课质量评分与统计
-- -----------------------------------------------------

DROP TABLE IF EXISTS `timetable_quality`;
CREATE TABLE `timetable_quality` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `version_id` BIGINT NOT NULL,
    `main_coverage_rate` DECIMAL(5, 2) DEFAULT NULL,
    `teacher_balance_score` DECIMAL(5, 2) DEFAULT NULL,
    `subject_balance_score` DECIMAL(5, 2) DEFAULT NULL,
    `room_utilization` DECIMAL(5, 2) DEFAULT NULL,
    `cycle_score` DECIMAL(5, 2) DEFAULT NULL,
    `consecutive_score` DECIMAL(5, 2) DEFAULT NULL,
    `total_score` DECIMAL(5, 2) DEFAULT NULL,
    `detail` JSON DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_version` (`version_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课表质量评分表';

DROP TABLE IF EXISTS `subject_weekly_plan`;
CREATE TABLE `subject_weekly_plan` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `academic_year_id` BIGINT NOT NULL,
    `semester_id` BIGINT NOT NULL,
    `class_id` BIGINT NOT NULL,
    `subject_id` BIGINT NOT NULL,
    `weekly_hours` INT NOT NULL DEFAULT 0,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_class_subject` (`class_id`, `subject_id`, `semester_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='班级周课时计划';

SET FOREIGN_KEY_CHECKS = 1;
