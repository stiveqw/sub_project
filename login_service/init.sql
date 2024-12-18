-- Create databases
CREATE DATABASE IF NOT EXISTS `course_db`;
CREATE DATABASE IF NOT EXISTS `user_db`;
CREATE DATABASE IF NOT EXISTS `notice_db`;
CREATE DATABASE IF NOT EXISTS `festival_db`;

-- Set character set and collation
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET collation_connection = utf8mb4_0900_ai_ci;

-- Switch to course_db
USE `course_db`;

-- Create courses table
CREATE TABLE `courses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_key` varchar(50) NOT NULL,
  `course_name` varchar(255) NOT NULL,
  `professor` varchar(255) NOT NULL,
  `max_students` int NOT NULL,
  `current_students` int DEFAULT '0',
  `credits` int NOT NULL,
  `department` varchar(100) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_key` (`course_key`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert data into courses
INSERT INTO `courses` VALUES (1,'CSE101','Introduction to Computer Science','Dr. Kim',50,0,3,'Computer Science',2024,'2024-11-29 16:45:49'),(2,'MAT201','Calculus II','Dr. Lee',30,0,3,'Mathematics',2024,'2024-11-29 16:45:49'),(3,'PHY301','Physics III','Dr. Park',25,0,4,'Physics',2024,'2024-11-29 16:45:49'),(4,'CHE102','General Chemistry','Dr. Choi',40,0,3,'Chemistry',2024,'2024-11-29 16:45:49'),(5,'BIO202','Molecular Biology','Dr. Yoon',35,0,3,'Biology',2024,'2024-11-29 16:45:49');

-- Create students table
CREATE TABLE `students` (
  `id` int NOT NULL,
  `student_id` varchar(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone_number` varchar(15) NOT NULL,
  `department` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert data into students
INSERT INTO `students` VALUES (12,'20230001','John Doe','john.doe@example.com','01012345678','Computer Science','2024-11-29 16:40:35'),(13,'20230002','Jane Smith','jane.smith@example.com','01023456789','Mathematics','2024-11-29 16:40:35'),(14,'20230003','Alice Kim','alice.kim@example.com','01034567890','Physics','2024-11-29 16:40:35'),(15,'20230004','Bob Lee','bob.lee@example.com','01045678901','Chemistry','2024-11-29 16:40:35'),(16,'20230005','Charlie Park','charlie.park@example.com','01056789012','Biology','2024-11-29 16:40:35');

-- Create registrations table
CREATE TABLE `registrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_key` varchar(50) NOT NULL,
  `student_id` varchar(20) NOT NULL,
  `registration_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('Applied','Cancelled') DEFAULT 'Applied',
  PRIMARY KEY (`id`),
  KEY `student_id` (`student_id`),
  KEY `course_key` (`course_key`),
  CONSTRAINT `registrations_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`),
  CONSTRAINT `registrations_ibfk_2` FOREIGN KEY (`course_key`) REFERENCES `courses` (`course_key`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert data into registrations
INSERT INTO `registrations` VALUES (6,'CSE101','20230001','2024-11-29 16:47:50','Applied'),(7,'MAT201','20230002','2024-11-29 16:47:50','Applied'),(8,'PHY301','20230003','2024-11-29 16:47:50','Cancelled'),(9,'CHE102','20230004','2024-11-29 16:47:50','Applied'),(10,'BIO202','20230005','2024-11-29 16:47:50','Applied');

-- Switch to user_db
USE `user_db`;

-- Create users table
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `student_id` varchar(20) NOT NULL,
  `department` varchar(100) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone_number` varchar(15) NOT NULL,
  `password_hash` text NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `student_id` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert data into users
INSERT INTO `users` VALUES (12,'20230001','Computer Science','John Doe','john.doe@example.com','01012345678','hashed_password_1','2024-11-29 16:40:35'),(13,'20230002','Mathematics','Jane Smith','jane.smith@example.com','01023456789','hashed_password_2','2024-11-29 16:40:35'),(14,'20230003','Physics','Alice Kim','alice.kim@example.com','01034567890','hashed_password_3','2024-11-29 16:40:35'),(15,'20230004','Chemistry','Bob Lee','bob.lee@example.com','01045678901','hashed_password_4','2024-11-29 16:40:35'),(16,'20230005','Biology','Charlie Park','charlie.park@example.com','01056789012','hashed_password_5','2024-11-29 16:40:35');

-- Create triggers for user_db
DELIMITER ;;

CREATE TRIGGER `sync_to_festival_users_insert` AFTER INSERT ON `users` FOR EACH ROW BEGIN
    INSERT INTO `festival_db`.users (user_id, name, email, phone_number, created_at)
    VALUES (NEW.user_id, NEW.name, NEW.email, NEW.phone_number, NEW.created_at)
    ON DUPLICATE KEY UPDATE
        name = NEW.name,
        email = NEW.email,
        phone_number = NEW.phone_number,
        created_at = NEW.created_at;
END;;

CREATE TRIGGER `sync_to_students_insert` AFTER INSERT ON `users` FOR EACH ROW BEGIN
    INSERT INTO `course_db`.students (id, student_id, name, email, phone_number, department, created_at)
    VALUES (NEW.user_id, NEW.student_id, NEW.name, NEW.email, NEW.phone_number, NEW.department, NEW.created_at)
    ON DUPLICATE KEY UPDATE
        name = NEW.name,
        email = NEW.email,
        phone_number = NEW.phone_number,
        department = NEW.department,
        created_at = NEW.created_at;
END;;

CREATE TRIGGER `sync_to_festival_users_update` AFTER UPDATE ON `users` FOR EACH ROW BEGIN
    INSERT INTO `festival_db`.users (user_id, name, email, phone_number, created_at)
    VALUES (NEW.user_id, NEW.name, NEW.email, NEW.phone_number, NEW.created_at)
    ON DUPLICATE KEY UPDATE
        name = NEW.name,
        email = NEW.email,
        phone_number = NEW.phone_number,
        created_at = NEW.created_at;
END;;

CREATE TRIGGER `sync_to_students_update` AFTER UPDATE ON `users` FOR EACH ROW BEGIN
    INSERT INTO `course_db`.students (id, student_id, name, email, phone_number, department, created_at)
    VALUES (NEW.user_id, NEW.student_id, NEW.name, NEW.email, NEW.phone_number, NEW.department, NEW.created_at)
    ON DUPLICATE KEY UPDATE
        name = NEW.name,
        email = NEW.email,
        phone_number = NEW.phone_number,
        department = NEW.department,
        created_at = NEW.created_at;
END;;

CREATE TRIGGER `sync_to_festival_users_delete` AFTER DELETE ON `users` FOR EACH ROW BEGIN
    DELETE FROM `festival_db`.users WHERE user_id = OLD.user_id;
END;;

CREATE TRIGGER `sync_to_students_delete` AFTER DELETE ON `users` FOR EACH ROW BEGIN
    DELETE FROM `course_db`.students WHERE id = OLD.user_id;
END;;

DELIMITER ;

-- Switch to notice_db
USE `notice_db`;

-- Create notices table
CREATE TABLE `notices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `date` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert data into notices
INSERT INTO `notices` VALUES (1,'System Maintenance Notice','The system will undergo maintenance on December 1st from 1:00 AM to 4:00 AM.','2024-12-01'),(2,'Holiday Announcement','The office will be closed for the holidays from December 24th to January 1st.','2024-12-20'),(3,'New Course Available','A new course on Data Science has been added to the curriculum. Check it out now!','2024-11-29'),(4,'Event Update','The annual cultural festival has been rescheduled to December 10th.','2024-11-28'),(5,'Policy Change','There have been updates to the refund policy. Please read the updated terms.','2024-11-25');

-- Switch to festival_db
USE `festival_db`;

-- Create festivals table
CREATE TABLE `festivals` (
  `id` int NOT NULL AUTO_INCREMENT,
  `festival_key` varchar(50) NOT NULL,
  `title` varchar(255) NOT NULL,
  `total_seats` int NOT NULL,
  `capacity` int NOT NULL,
  `date` datetime NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `festival_key` (`festival_key`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert data into festivals
INSERT INTO `festivals` VALUES (1,'FEST001','Spring Festival',500,300,'2024-03-15 10:00:00','2024-11-29 11:00:36'),(2,'FEST002','Summer Music Fest',1000,800,'2024-06-20 18:00:00','2024-11-29 11:00:36'),(3,'FEST003','Autumn Food Fest',300,250,'2024-09-10 12:00:00','2024-11-29 11:00:36'),(4,'FEST004','Winter Wonderland',700,600,'2024-12-05 17:00:00','2024-11-29 11:00:36'),(5,'FEST005','Cultural Night',200,150,'2024-11-25 19:30:00','2024-11-29 11:00:36');

-- Create users table for festival_db
CREATE TABLE `users` (
  `user_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone_number` varchar(15) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert data into users for festival_db
INSERT INTO `users` VALUES (7,'John Doe','john.doe@example.com','01012345678','2024-11-29 10:57:26'),(8,'Jane Smith','jane.smith@example.com','01023456789','2024-11-29 10:57:26'),(9,'Alice Kim','alice.kim@example.com','01034567890','2024-11-29 10:57:26'),(10,'Bob Lee','bob.lee@example.com','01045678901','2024-11-29 10:57:26'),(11,'Charlie Park','charlie.park@example.com','01056789012','2024-11-29 10:57:26');

-- Create reservations table
CREATE TABLE `reservations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `festival_key` varchar(50) NOT NULL,
  `user_id` int NOT NULL,
  `seat_number` varchar(20) NOT NULL,
  `status` enum('Reserved','Cancelled') DEFAULT 'Reserved',
  `reservation_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `festival_key` (`festival_key`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `reservations_ibfk_1` FOREIGN KEY (`festival_key`) REFERENCES `festivals` (`festival_key`),
  CONSTRAINT `reservations_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert data into reservations
INSERT INTO `reservations` VALUES (1,'FEST001',7,'A1','Reserved','2024-11-29 11:00:42'),(2,'FEST002',8,'B12','Reserved','2024-11-29 11:00:42'),(3,'FEST003',9,'C5','Reserved','2024-11-29 11:00:42'),(4,'FEST004',10,'D20','Cancelled','2024-11-29 11:00:42'),(5,'FEST005',11,'E8','Reserved','2024-11-29 11:00:42');