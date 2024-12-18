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
INSERT INTO `students` (`id`, `student_id`, `name`, `email`, `phone_number`, `department`, `created_at`) VALUES
(12,'20230001','John Doe','john.doe@example.com','01012345678','Computer Science','2024-11-29 16:40:35'),
(13,'20230002','Jane Smith','jane.smith@example.com','01023456789','Mathematics','2024-11-29 16:40:35'),
(14,'20230003','Alice Kim','alice.kim@example.com','01034567890','Physics','2024-11-29 16:40:35'),
(15,'20230004','Bob Lee','bob.lee@example.com','01045678901','Chemistry','2024-11-29 16:40:35'),
(16,'20230005','Charlie Park','charlie.park@example.com','01056789012','Biology','2024-11-29 16:40:35'),
(17,'20230006','Charlie Park1','charlie.park1@example.com','01056789013','Biology','2024-11-29 16:40:36'),
(18,'20230007','Charlie Park2','charlie.park2@example.com','01056789014','Biology','2024-11-29 16:40:37'),
(19,'20230008','Charlie Park3','charlie.park3@example.com','01056789015','Biology','2024-11-29 16:40:38'),
(20,'20230009','Charlie Park4','charlie.park4@example.com','01056789016','Biology','2024-11-29 16:40:39'),
(21,'202300010','Charlie Park5','charlie.park5@example.com','01056789017','Biology','2024-11-29 16:40:41'),
(22,'20230011','Charlie Park6','charlie.park6@example.com','01056789018','Biology','2024-11-29 16:40:40'),
(23,'20230012','Charlie Park7','charlie.park7@example.com','01056789019','Biology','2024-11-29 16:40:44'),
(24,'20230013','Student 24','student24@example.com','01067890123','Engineering','2024-11-29 16:40:45'),
(25,'20230014','Student 25','student25@example.com','01078901234','Economics','2024-11-29 16:40:46'),
(26,'20230015','Student 26','student26@example.com','01089012345','Psychology','2024-11-29 16:40:47'),
(27,'20230016','Student 27','student27@example.com','01090123456','Literature','2024-11-29 16:40:48'),
(28,'20230017','Student 28','student28@example.com','01001234567','History','2024-11-29 16:40:49'),
(29,'20230018','Student 29','student29@example.com','01012345678','Computer Science','2024-11-29 16:40:50'),
(30,'20230019','Student 30','student30@example.com','01023456789','Mathematics','2024-11-29 16:40:51'),
(31,'20230020','Student 31','student31@example.com','01034567890','Physics','2024-11-29 16:40:52'),
(32,'20230021','Student 32','student32@example.com','01045678901','Chemistry','2024-11-29 16:40:53'),
(33,'20230022','Student 33','student33@example.com','01056789012','Biology','2024-11-29 16:40:54'),
(34,'20230023','Student 34','student34@example.com','01067890123','Engineering','2024-11-29 16:40:55'),
(35,'20230024','Student 35','student35@example.com','01078901234','Economics','2024-11-29 16:40:56'),
(36,'20230025','Student 36','student36@example.com','01089012345','Psychology','2024-11-29 16:40:57'),
(37,'20230026','Student 37','student37@example.com','01090123456','Literature','2024-11-29 16:40:58'),
(38,'20230027','Student 38','student38@example.com','01001234567','History','2024-11-29 16:40:59'),
(39,'20230028','Student 39','student39@example.com','01012345678','Computer Science','2024-11-29 16:41:00'),
(40,'20230029','Student 40','student40@example.com','01023456789','Mathematics','2024-11-29 16:41:01'),
(41,'20230030','Student 41','student41@example.com','01034567890','Physics','2024-11-29 16:41:02'),
(42,'20230031','Student 42','student42@example.com','01045678901','Chemistry','2024-11-29 16:41:03'),
(43,'20230032','Student 43','student43@example.com','01056789012','Biology','2024-11-29 16:41:04'),
(44,'20230033','Student 44','student44@example.com','01067890123','Engineering','2024-11-29 16:41:05'),
(45,'20230034','Student 45','student45@example.com','01078901234','Economics','2024-11-29 16:41:06'),
(46,'20230035','Student 46','student46@example.com','01089012345','Psychology','2024-11-29 16:41:07'),
(47,'20230036','Student 47','student47@example.com','01090123456','Literature','2024-11-29 16:41:08'),
(48,'20230037','Student 48','student48@example.com','01001234567','History','2024-11-29 16:41:09'),
(49,'20230038','Student 49','student49@example.com','01012345678','Computer Science','2024-11-29 16:41:10'),
(50,'20230039','Student 50','student50@example.com','01023456789','Mathematics','2024-11-29 16:41:11'),
(51,'20230040','Student 51','student51@example.com','01034567890','Physics','2024-11-29 16:41:12'),
(52,'20230041','Student 52','student52@example.com','01045678901','Chemistry','2024-11-29 16:41:13'),
(53,'20230042','Student 53','student53@example.com','01056789012','Biology','2024-11-29 16:41:14'),
(54,'20230043','Student 54','student54@example.com','01067890123','Engineering','2024-11-29 16:41:15'),
(55,'20230044','Student 55','student55@example.com','01078901234','Economics','2024-11-29 16:41:16'),
(56,'20230045','Student 56','student56@example.com','01089012345','Psychology','2024-11-29 16:41:17'),
(57,'20230046','Student 57','student57@example.com','01090123456','Literature','2024-11-29 16:41:18'),
(58,'20230047','Student 58','student58@example.com','01001234567','History','2024-11-29 16:41:19'),
(59,'20230048','Student 59','student59@example.com','01012345678','Computer Science','2024-11-29 16:41:20'),
(60,'20230049','Student 60','student60@example.com','01023456789','Mathematics','2024-11-29 16:41:21'),
(61,'20230050','Student 61','student61@example.com','01034567890','Physics','2024-11-29 16:41:22'),
(62,'20230051','Student 62','student62@example.com','01045678901','Chemistry','2024-11-29 16:41:23'),
(63,'20230052','Student 63','student63@example.com','01056789012','Biology','2024-11-29 16:41:24'),
(64,'20230053','Student 64','student64@example.com','01067890123','Engineering','2024-11-29 16:41:25'),
(65,'20230054','Student 65','student65@example.com','01078901234','Economics','2024-11-29 16:41:26'),
(66,'20230055','Student 66','student66@example.com','01089012345','Psychology','2024-11-29 16:41:27'),
(67,'20230056','Student 67','student67@example.com','01090123456','Literature','2024-11-29 16:41:28'),
(68,'20230057','Student 68','student68@example.com','01001234567','History','2024-11-29 16:41:29'),
(69,'20230058','Student 69','student69@example.com','01012345678','Computer Science','2024-11-29 16:41:30'),
(70,'20230059','Student 70','student70@example.com','01023456789','Mathematics','2024-11-29 16:41:31'),
(71,'20230060','Student 71','student71@example.com','01034567890','Physics','2024-11-29 16:41:32'),
(72,'20230061','Student 72','student72@example.com','01045678901','Chemistry','2024-11-29 16:41:33'),
(73,'20230062','Student 73','student73@example.com','01056789012','Biology','2024-11-29 16:41:34'),
(74,'20230063','Student 74','student74@example.com','01067890123','Engineering','2024-11-29 16:41:35'),
(75,'20230064','Student 75','student75@example.com','01078901234','Economics','2024-11-29 16:41:36'),
(76,'20230065','Student 76','student76@example.com','01089012345','Psychology','2024-11-29 16:41:37'),
(77,'20230066','Student 77','student77@example.com','01090123456','Literature','2024-11-29 16:41:38'),
(78,'20230067','Student 78','student78@example.com','01001234567','History','2024-11-29 16:41:39'),
(79,'20230068','Student 79','student79@example.com','01012345678','Computer Science','2024-11-29 16:41:40'),
(80,'20230069','Student 80','student80@example.com','01023456789','Mathematics','2024-11-29 16:41:41'),
(81,'20230070','Student 81','student81@example.com','01034567890','Physics','2024-11-29 16:41:42'),
(82,'20230071','Student 82','student82@example.com','01045678901','Chemistry','2024-11-29 16:41:43'),
(83,'20230072','Student 83','student83@example.com','01056789012','Biology','2024-11-29 16:41:44'),
(84,'20230073','Student 84','student84@example.com','01067890123','Engineering','2024-11-29 16:41:45'),
(85,'20230074','Student 85','student85@example.com','01078901234','Economics','2024-11-29 16:41:46'),
(86,'20230075','Student 86','student86@example.com','01089012345','Psychology','2024-11-29 16:41:47'),
(87,'20230076','Student 87','student87@example.com','01090123456','Literature','2024-11-29 16:41:48'),
(88,'20230077','Student 88','student88@example.com','01001234567','History','2024-11-29 16:41:49'),
(89,'20230078','Student 89','student89@example.com','01012345678','Computer Science','2024-11-29 16:41:50'),
(90,'20230079','Student 90','student90@example.com','01023456789','Mathematics','2024-11-29 16:41:51'),
(91,'20230080','Student 91','student91@example.com','01034567890','Physics','2024-11-29 16:41:52'),
(92,'20230081','Student 92','student92@example.com','01045678901','Chemistry','2024-11-29 16:41:53'),
(93,'20230082','Student 93','student93@example.com','01056789012','Biology','2024-11-29 16:41:54'),
(94,'20230083','Student 94','student94@example.com','01067890123','Engineering','2024-11-29 16:41:55'),
(95,'20230084','Student 95','student95@example.com','01078901234','Economics','2024-11-29 16:41:56'),
(96,'20230085','Student 96','student96@example.com','01089012345','Psychology','2024-11-29 16:41:57'),
(97,'20230086','Student 97','student97@example.com','01090123456','Literature','2024-11-29 16:41:58'),
(98,'20230087','Student 98','student98@example.com','01001234567','History','2024-11-29 16:41:59'),
(99,'20230088','Student 99','student99@example.com','01012345678','Computer Science','2024-11-29 16:42:00'),
(100,'20230089','Student 100','student100@example.com','01023456789','Mathematics','2024-11-29 16:42:01'),
(101,'20230090','Student 101','student101@example.com','01034567890','Physics','2024-11-29 16:42:02'),
(102,'20230091','Student 102','student102@example.com','01045678901','Chemistry','2024-11-29 16:42:03'),
(103,'20230092','Student 103','student103@example.com','01056789012','Biology','2024-11-29 16:42:04');


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