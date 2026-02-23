-- Rollback: init_unsigned_ids
-- Description: Reverts initial schema creation

-- Drop foreign keys first
ALTER TABLE `password_reset_tokens` DROP FOREIGN KEY `password_reset_tokens_user_id_fkey`;
ALTER TABLE `user_progress` DROP FOREIGN KEY `user_progress_username_fkey`;
ALTER TABLE `module_question_imports` DROP FOREIGN KEY `module_question_imports_module_id_fkey`;
ALTER TABLE `module_questions` DROP FOREIGN KEY `module_questions_module_id_fkey`;

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS `password_reset_tokens`;
DROP TABLE IF EXISTS `revoked_tokens`;
DROP TABLE IF EXISTS `user_progress`;
DROP TABLE IF EXISTS `users`;
DROP TABLE IF EXISTS `module_question_imports`;
DROP TABLE IF EXISTS `module_questions`;
DROP TABLE IF EXISTS `modules`;
