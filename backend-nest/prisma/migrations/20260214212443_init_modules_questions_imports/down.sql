-- Rollback: init_modules_questions_imports
-- Description: Reverts the initial 3 tables creation
-- Date: 2026-02-15
--
-- IMPORTANT: Tables must be dropped in reverse dependency order
-- module_question_imports depends on modules (FK)
-- module_questions depends on modules (FK)
-- modules has no dependencies

-- ─── Drop foreign keys first ─────────────────────────────────────────────────

ALTER TABLE `module_question_imports` DROP FOREIGN KEY `module_question_imports_module_id_fkey`;
ALTER TABLE `module_questions` DROP FOREIGN KEY `module_questions_module_id_fkey`;

-- ─── Drop Table 3: module_question_imports ───────────────────────────────────

DROP TABLE IF EXISTS `module_question_imports`;

-- ─── Drop Table 2: module_questions ──────────────────────────────────────────

DROP TABLE IF EXISTS `module_questions`;

-- ─── Drop Table 1: modules ──────────────────────────────────────────────────

DROP TABLE IF EXISTS `modules`;
