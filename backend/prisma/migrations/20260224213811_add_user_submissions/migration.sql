-- CreateTable
CREATE TABLE `user_submissions` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(50) NOT NULL,
    `question_id` VARCHAR(50) NOT NULL,
    `submitted_code` TEXT NULL,
    `stdout` TEXT NULL,
    `stderr` TEXT NULL,
    `status` VARCHAR(10) NOT NULL,
    `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),

    INDEX `idx_us_username`(`username`),
    INDEX `idx_us_username_question`(`username`, `question_id`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `user_submissions` ADD CONSTRAINT `user_submissions_username_fkey` FOREIGN KEY (`username`) REFERENCES `users`(`username`) ON DELETE CASCADE ON UPDATE CASCADE;
