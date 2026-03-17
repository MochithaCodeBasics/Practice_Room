/*
  Warnings:

  - You are about to drop the column `username` on the `user_submissions` table. All the data in the column will be lost.
  - Added the required column `user_id` to the `user_submissions` table without a default value. This is not possible if the table is not empty.

*/
-- Clear user_submissions: username→user_id mapping is not possible, data cannot be migrated
DELETE FROM `user_submissions`;

-- DropForeignKey
ALTER TABLE `user_submissions` DROP FOREIGN KEY `user_submissions_username_fkey`;

-- DropIndex
DROP INDEX `idx_us_username` ON `user_submissions`;

-- DropIndex
DROP INDEX `idx_us_username_question` ON `user_submissions`;

-- AlterTable
ALTER TABLE `user_submissions` DROP COLUMN `username`,
    ADD COLUMN `user_id` INTEGER NOT NULL;

-- CreateIndex
CREATE INDEX `idx_us_user_id` ON `user_submissions`(`user_id`);

-- CreateIndex
CREATE INDEX `idx_us_user_id_question` ON `user_submissions`(`user_id`, `question_id`);

-- AddForeignKey
ALTER TABLE `user_submissions` ADD CONSTRAINT `user_submissions_user_id_fkey` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;
