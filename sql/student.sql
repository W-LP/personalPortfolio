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
  `personality` VARCHAR(500)  DEFAULT NULL COMMENT '性格特点',
  `createtime`  DATETIME      DEFAULT NULL COMMENT '创建时间',
  `updatetime`  DATETIME      DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_student_studentname` (`studentname`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '学生信息表';

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
