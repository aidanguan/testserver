-- 基于Web的自然语言驱动UI测试平台数据库初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS ui_test_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ui_test_platform;

-- 用户表
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('Admin', 'Member') NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    INDEX idx_username (`username`),
    INDEX idx_role (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 项目表
CREATE TABLE IF NOT EXISTS `project` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL UNIQUE,
    `description` TEXT,
    `base_url` VARCHAR(500) NOT NULL,
    `llm_provider` VARCHAR(50) NOT NULL,
    `llm_model` VARCHAR(100) NOT NULL,
    `llm_api_key` VARCHAR(255) NOT NULL,
    `llm_config` JSON,
    `created_by` INT NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`created_by`) REFERENCES `user`(`id`) ON DELETE RESTRICT,
    INDEX idx_name (`name`),
    INDEX idx_created_by (`created_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目表';

-- 测试用例表
CREATE TABLE IF NOT EXISTS `test_case` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `project_id` INT NOT NULL,
    `name` VARCHAR(200) NOT NULL,
    `description` TEXT,
    `natural_language` TEXT NOT NULL,
    `standard_steps` JSON NOT NULL,
    `playwright_script` JSON NOT NULL,
    `expected_result` TEXT NOT NULL,
    `created_by` INT NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`project_id`) REFERENCES `project`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`created_by`) REFERENCES `user`(`id`) ON DELETE RESTRICT,
    INDEX idx_project_id (`project_id`),
    INDEX idx_created_by (`created_by`),
    INDEX idx_name (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试用例表';

-- 运行记录表
CREATE TABLE IF NOT EXISTS `test_run` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `test_case_id` INT NOT NULL,
    `status` ENUM('running', 'success', 'failed', 'error') NOT NULL,
    `trigger_by` INT NOT NULL,
    `start_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `end_time` DATETIME,
    `llm_verdict` ENUM('passed', 'failed', 'unknown'),
    `llm_reason` TEXT,
    `error_message` TEXT,
    `artifacts_path` VARCHAR(500),
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`test_case_id`) REFERENCES `test_case`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`trigger_by`) REFERENCES `user`(`id`) ON DELETE RESTRICT,
    INDEX idx_test_case_id (`test_case_id`),
    INDEX idx_trigger_by (`trigger_by`),
    INDEX idx_status (`status`),
    INDEX idx_start_time (`start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='运行记录表';

-- 步骤执行记录表
CREATE TABLE IF NOT EXISTS `step_execution` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `test_run_id` INT NOT NULL,
    `step_index` INT NOT NULL,
    `step_description` TEXT NOT NULL,
    `status` ENUM('success', 'failed', 'skipped') NOT NULL,
    `screenshot_path` VARCHAR(500),
    `start_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `end_time` DATETIME,
    `error_message` TEXT,
    FOREIGN KEY (`test_run_id`) REFERENCES `test_run`(`id`) ON DELETE CASCADE,
    INDEX idx_test_run_id (`test_run_id`),
    INDEX idx_step_index (`step_index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='步骤执行记录表';

-- 审计日志表
CREATE TABLE IF NOT EXISTS `audit_log` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `action` VARCHAR(100) NOT NULL,
    `resource_type` VARCHAR(50) NOT NULL,
    `resource_id` INT,
    `details` JSON,
    `ip_address` VARCHAR(50),
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE RESTRICT,
    INDEX idx_user_id (`user_id`),
    INDEX idx_action (`action`),
    INDEX idx_resource_type (`resource_type`),
    INDEX idx_created_at (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审计日志表';

-- 插入默认管理员账号 (密码: admin, 使用bcrypt哈希)
-- bcrypt哈希值: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIRSk7HRnW (对应密码: admin)
INSERT INTO `user` (`username`, `password_hash`, `role`, `is_active`) 
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIRSk7HRnW', 'Admin', TRUE)
ON DUPLICATE KEY UPDATE `username` = `username`;
