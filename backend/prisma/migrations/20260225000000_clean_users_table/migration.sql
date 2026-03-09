-- Clean users table: remove credential/LLM/streak fields, add cb_user_id
-- Remove PasswordResetToken table (no longer needed with CB-only auth)
-- Migrate user_progress FK from username → user_id

-- Drop password_reset_tokens (CB auth has no passwords to reset)
DROP TABLE IF EXISTS `password_reset_tokens`;

-- Drop old user_progress indexes and constraints
DROP INDEX `idx_up_username` ON `user_progress`;
DROP INDEX `username_question_id` ON `user_progress`;

-- Add user_id to user_progress and remove username
ALTER TABLE `user_progress`
    ADD COLUMN `user_id` INT NOT NULL AFTER `id`,
    DROP COLUMN `username`;

-- Add FK and new unique index on user_progress
ALTER TABLE `user_progress`
    ADD CONSTRAINT `user_progress_user_id_fkey` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

CREATE UNIQUE INDEX `user_id_question_id` ON `user_progress`(`user_id`, `question_id`);
CREATE INDEX `idx_up_user_id` ON `user_progress`(`user_id`);

-- Drop credential, LLM and streak columns from users
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
