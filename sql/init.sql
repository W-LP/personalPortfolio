-- ============================================================
-- 个人作品集网站 - MySQL 初始化脚本
-- 适用: 宝塔面板 -> 数据库 -> root 账户导入，或 phpMyAdmin 导入
-- ============================================================

-- 1. 创建数据库（utf8mb4 支持 emoji 和中文）
CREATE DATABASE IF NOT EXISTS `portfolio`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE `portfolio`;

-- 2. 创建应用账号（按需修改密码，与后端 application.yml 保持一致）
CREATE USER IF NOT EXISTS 'portfolio'@'localhost' IDENTIFIED BY 'portfolio123';
CREATE USER IF NOT EXISTS 'portfolio'@'%' IDENTIFIED BY 'portfolio123';
GRANT ALL PRIVILEGES ON `portfolio`.* TO 'portfolio'@'localhost';
GRANT ALL PRIVILEGES ON `portfolio`.* TO 'portfolio'@'%';
FLUSH PRIVILEGES;

-- 3. 项目表（后端 jpa ddl-auto=update 时也会自动创建，此脚本保证结构可控）
DROP TABLE IF EXISTS `project`;
CREATE TABLE `project` (
  `id`          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
  `title`       VARCHAR(100) NOT NULL COMMENT '项目标题',
  `description` VARCHAR(1000) DEFAULT NULL COMMENT '项目简介',
  `tech_stack`  VARCHAR(255)  DEFAULT NULL COMMENT '技术栈，逗号分隔',
  `link`        VARCHAR(500)  DEFAULT NULL COMMENT '项目链接',
  `sort_order`  INT           DEFAULT 0 COMMENT '展示排序，越小越靠前',
  `created_at`  DATETIME(6)   DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '作品集项目表';

-- 4. 示例数据
INSERT INTO `project` (`title`, `description`, `tech_stack`, `link`, `sort_order`, `created_at`) VALUES
('个人作品集网站', '本网站：Vue 3 前端 + Spring Boot 后端 + MySQL，部署在宝塔面板。', 'Vue,Java,MySQL,Nginx', 'https://example.com', 1, NOW()),
('待添加项目二', '这里是第二个项目的简介。', 'Vue,Java', '', 2, NOW());
