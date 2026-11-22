-- ========================================================
-- Domain-Specific RAG Assistant for AWS Technical Support
-- MySQL Database Schema
-- ========================================================

CREATE DATABASE IF NOT EXISTS `aws_support_rag` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `aws_support_rag`;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` VARCHAR(20) NOT NULL DEFAULT 'user',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `last_login` TIMESTAMP NULL DEFAULT NULL,
    INDEX `idx_username` (`username`),
    INDEX `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Chat Sessions Table
CREATE TABLE IF NOT EXISTS `chat_sessions` (
    `id` VARCHAR(64) PRIMARY KEY,
    `user_id` INT NOT NULL,
    `title` VARCHAR(255) NOT NULL DEFAULT 'AWS Support Session',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_session_user` (`user_id`),
    CONSTRAINT `fk_sessions_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Chat History & RAG Query Logging Table
CREATE TABLE IF NOT EXISTS `chat_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `session_id` VARCHAR(64) NULL,
    `user_id` INT NOT NULL,
    `query` TEXT NOT NULL,
    `response` MEDIUMTEXT NOT NULL,
    `intent` VARCHAR(50) DEFAULT 'GENERAL',
    `service` VARCHAR(50) DEFAULT 'General AWS',
    `urgency` VARCHAR(20) DEFAULT 'LOW',
    `is_grounded` TINYINT(1) DEFAULT 1,
    `latency_ms` FLOAT DEFAULT 0.0,
    `sources_json` TEXT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_history_user` (`user_id`, `created_at`),
    INDEX `idx_history_service` (`service`),
    INDEX `idx_history_intent` (`intent`),
    CONSTRAINT `fk_history_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Security Audit Logs Table
CREATE TABLE IF NOT EXISTS `audit_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NULL,
    `event_type` VARCHAR(50) NOT NULL,
    `ip_address` VARCHAR(50) NULL DEFAULT '127.0.0.1',
    `details` TEXT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_audit_user` (`user_id`),
    INDEX `idx_audit_time` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Seed default demo and admin accounts (passwords hashed via bcrypt: 'Demo1234!' and 'Admin1234!')
-- Note: Python AuthService also auto-seeds these if not present
INSERT IGNORE INTO `users` (`id`, `username`, `email`, `password_hash`, `role`) VALUES
(1, 'demouser', 'demo@awssupport.internal', '$2b$12$eXAMPLeHashForDemoPasswordNotUsedDirectlyDemo1234567890', 'user'),
(2, 'admin', 'admin@awssupport.internal', '$2b$12$eXAMPLeHashForAdminPasswordNotUsedDirectlyAdmin1234567890', 'admin');

