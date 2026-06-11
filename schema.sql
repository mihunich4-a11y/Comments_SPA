-- Comments SPA — Schema
-- Compatible with MySQL Workbench

CREATE TABLE IF NOT EXISTS `comments_user` (
    `id`         INTEGER      NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `username`   VARCHAR(50)  NOT NULL,
    `email`      VARCHAR(254) NOT NULL,
    `home_page`  VARCHAR(200) NULL,
    `ip_address` VARCHAR(39)  NOT NULL,
    `user_agent` TEXT         NOT NULL,
    `created_at` DATETIME     NOT NULL,
    UNIQUE KEY `uq_username_email` (`username`, `email`)
);

CREATE TABLE IF NOT EXISTS `comments_comment` (
    `id`         INTEGER  NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `user_id`    INTEGER  NOT NULL,
    `parent_id`  INTEGER  NULL,
    `text`       LONGTEXT NOT NULL,
    `image`      VARCHAR(100) NULL,
    `txt_file`   VARCHAR(100) NULL,
    `created_at` DATETIME NOT NULL,
    CONSTRAINT `fk_comment_user`
        FOREIGN KEY (`user_id`)
        REFERENCES `comments_user` (`id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_comment_parent`
        FOREIGN KEY (`parent_id`)
        REFERENCES `comments_comment` (`id`)
        ON DELETE CASCADE
);

CREATE INDEX `idx_comment_user`   ON `comments_comment` (`user_id`);
CREATE INDEX `idx_comment_parent` ON `comments_comment` (`parent_id`);
CREATE INDEX `idx_comment_date`   ON `comments_comment` (`created_at`);
CREATE INDEX `idx_user_email`     ON `comments_user` (`email`);
