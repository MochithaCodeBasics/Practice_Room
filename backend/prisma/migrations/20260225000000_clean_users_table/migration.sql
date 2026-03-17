-- Clean users table: remove credential/LLM/streak fields, add cb_user_id
-- Remove PasswordResetToken table (no longer needed with CB-only auth)
-- Migrate user_progress FK from username → user_id
--
-- NOTE: user_progress and users data cannot be migrated (no username→cb_user_id mapping exists).
-- Both tables are cleared before schema changes so NOT NULL columns can be added safely.

-- Drop password_reset_tokens (CB auth has no passwords to reset)
DROP TABLE IF EXISTS `password_reset_tokens`;

-- Clear user_progress first (FK dependency on users, and username→user_id mapping is not possible)
DELETE FROM `user_progress`;

-- Clear users (cb_user_id can only be populated after users re-authenticate via CB OAuth)
DELETE FROM `users`;

-- Drop FK on user_progress.username (conditional — safe if already dropped)
SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
               WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'user_progress'
               AND CONSTRAINT_NAME = 'user_progress_username_fkey' AND CONSTRAINT_TYPE = 'FOREIGN KEY');
SET @sql := IF(@exist > 0, 'ALTER TABLE `user_progress` DROP FOREIGN KEY `user_progress_username_fkey`', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop old user_progress indexes (MySQL has no DROP INDEX IF EXISTS — use INFORMATION_SCHEMA)
SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
               WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'user_progress' AND INDEX_NAME = 'idx_up_username');
SET @sql := IF(@exist > 0, 'DROP INDEX `idx_up_username` ON `user_progress`', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
               WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'user_progress' AND INDEX_NAME = 'user_progress_username_question_id_key');
SET @sql := IF(@exist > 0, 'DROP INDEX `user_progress_username_question_id_key` ON `user_progress`', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Add user_id to user_progress and remove username
-- Table is empty so NOT NULL is safe
ALTER TABLE `user_progress`
    ADD COLUMN `user_id` INT NOT NULL AFTER `id`,
    DROP COLUMN `username`;

-- Add FK and new unique index on user_progress
ALTER TABLE `user_progress`
    ADD CONSTRAINT `user_progress_user_id_fkey` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

CREATE UNIQUE INDEX `user_id_question_id` ON `user_progress`(`user_id`, `question_id`);
CREATE INDEX `idx_up_user_id` ON `user_progress`(`user_id`);

-- Drop credential, LLM and streak columns from users and add cb_user_id
-- Table is empty so NOT NULL is safe
ALTER TABLE `users`
    DROP COLUMN `username`,
    DROP COLUMN `hashed_password`,
    DROP COLUMN `disabled`,
    DROP COLUMN `groq_api_key`,
    DROP COLUMN `openai_api_key`,
    DROP COLUMN `anthropic_api_key`,
    DROP COLUMN `has_groq_api_key`,
    DROP COLUMN `has_openai_api_key`,
    DROP COLUMN `has_anthropic_api_key`,
    DROP COLUMN `default_llm_provider`,
    DROP COLUMN `current_streak`,
    DROP COLUMN `last_completed_at`,
    ADD COLUMN `cb_user_id` VARCHAR(50) NOT NULL;

-- Add unique constraint on cb_user_id
CREATE UNIQUE INDEX `users_cb_user_id_key` ON `users`(`cb_user_id`);
