-- ============================================================
-- AI 学管（教师辅助管理学生）- MySQL 初始化脚本
-- 功能：学生信息表 + 学生成绩表
-- 适用: 宝塔面板 -> 数据库 -> 导入，或 phpMyAdmin 导入
-- 作者: 6588 万立鹏
-- 日期: 2026-09-01
-- ============================================================

USE `portfolio`;

-- 1. 学生信息表（列名统一纯小写，单词直接拼接，与实体 @TableField 一致）
DROP TABLE IF EXISTS `student`;
CREATE TABLE `student` (
  `id`          BIGINT        NOT NULL AUTO_INCREMENT COMMENT '主键',
  `studentname` VARCHAR(50)   NOT NULL COMMENT '姓名（唯一标识，重复视为更新）',
  `gender`      VARCHAR(10)   DEFAULT NULL COMMENT '性别：男/女',
  `age`         INT           DEFAULT NULL COMMENT '年龄',
  `height`      DOUBLE        DEFAULT NULL COMMENT '身高(cm)',
  `weight`      DOUBLE        DEFAULT NULL COMMENT '体重(kg)',
  `personality` TEXT          DEFAULT NULL COMMENT '性格特点（多行文本）',
  `cohort`      INT           DEFAULT NULL COMMENT '届（数字，如 2026）',
  `grade`       INT           DEFAULT NULL COMMENT '年级（数字）',
  `classnum`    INT           DEFAULT NULL COMMENT '班级（数字）',
  `createtime`  DATETIME      DEFAULT NULL COMMENT '创建时间',
  `updatetime`  DATETIME      DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_student_studentname` (`studentname`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '学生信息表';

-- 历史库升级：student 表新增届/班级字段、性格改多行文本（全新安装可忽略）
-- ALTER TABLE `student` ADD COLUMN `cohort`    VARCHAR(20) DEFAULT NULL COMMENT '届（如 2026届）';
-- ALTER TABLE `student` ADD COLUMN `classname` VARCHAR(50) DEFAULT NULL COMMENT '班级（如 三年二班）';
-- ALTER TABLE `student` MODIFY COLUMN `personality` TEXT DEFAULT NULL COMMENT '性格特点（多行文本）';

-- 2. 学生成绩表（每次周练/月考按 考试名称+科目 录入）
DROP TABLE IF EXISTS `studentscore`;
CREATE TABLE `studentscore` (
  `id`          BIGINT        NOT NULL AUTO_INCREMENT COMMENT '主键',
  `studentid`   BIGINT        NOT NULL COMMENT '学生ID（关联 student.id）',
  `studentname` VARCHAR(50)   DEFAULT NULL COMMENT '姓名（冗余，便于展示）',
  `examname`    VARCHAR(100)  NOT NULL COMMENT '考试名称：第一次周练/9月月考等',
  `examdate`    DATE          DEFAULT NULL COMMENT '考试日期',
  `subject`     VARCHAR(50)   NOT NULL COMMENT '科目：语文/数学/英语等',
  `scorevalue`  DOUBLE        DEFAULT NULL COMMENT '分数',
  `createtime`  DATETIME      DEFAULT NULL COMMENT '创建时间',
  `updatetime`  DATETIME      DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_score_studentid` (`studentid`),
  KEY `idx_score_examname` (`examname`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '学生成绩表';

-- 3. 教师账号表（AI 学管登录/注册，密码存 SHA-256 加盐摘要）
DROP TABLE IF EXISTS `teacher`;
CREATE TABLE `teacher` (
  `id`            BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
  `username`      VARCHAR(20)  NOT NULL COMMENT '登录账号',
  `password`      VARCHAR(64)  NOT NULL COMMENT '密码摘要（SHA-256 加盐）',
  `realname`      VARCHAR(50)  DEFAULT NULL COMMENT '教师姓名',
  `subject`       VARCHAR(50)  DEFAULT NULL COMMENT '任教科目',
  `grade`         INT          DEFAULT NULL COMMENT '任教年级（数字）',
  `classnum`      INT          DEFAULT NULL COMMENT '任教班级（数字）',
  `isclassteacher` TINYINT     NOT NULL DEFAULT 0 COMMENT '是否该班级班主任（0否 1是）',
  `createtime`    DATETIME     DEFAULT NULL COMMENT '创建时间',
  `updatetime`    DATETIME     DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_teacher_username` (`username`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '教师账号表';

-- 历史库升级：teacher 表任教班级拆分为年级/班级数字字段（全新安装可忽略）
-- ALTER TABLE `teacher` ADD COLUMN `grade` INT DEFAULT NULL COMMENT '任教年级（数字）' AFTER `subject`;
-- ALTER TABLE `teacher` ADD COLUMN `classnum` INT DEFAULT NULL COMMENT '任教班级（数字）' AFTER `grade`;
-- ALTER TABLE `teacher` DROP COLUMN `classname`;

-- 历史库升级：学生字段数字化（届/年级/班级均为 INT，年级与班级拆分为两个字段，全新安装可忽略）
-- 注意：旧 classname 存过中文班级名时直接转换会丢数据，请先确认无需保留
-- ALTER TABLE `student` MODIFY COLUMN `cohort` INT DEFAULT NULL COMMENT '届（数字，如 2026）';
-- ALTER TABLE `student` ADD COLUMN `grade` INT DEFAULT NULL COMMENT '年级（数字）' AFTER `cohort`;
-- ALTER TABLE `student` ADD COLUMN `classnum` INT DEFAULT NULL COMMENT '班级（数字）' AFTER `grade`;
-- ALTER TABLE `student` DROP COLUMN `classname`;
