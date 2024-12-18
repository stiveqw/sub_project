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
-- Insert data into users
INSERT INTO `users` (`user_id`, `name`, `email`, `phone_number`, `created_at`) VALUES
(7, 'Alice Johnson', 'alice.johnson@example.com', '01023456789', '2024-11-29 16:40:35'),
(8, 'Bob Williams', 'bob.williams@example.com', '01034567890', '2024-11-29 16:40:36'),
(9, 'Carol Brown', 'carol.brown@example.com', '01045678901', '2024-11-29 16:40:37'),
(10, 'David Lee', 'david.lee@example.com', '01056789012', '2024-11-29 16:40:38'),
(11, 'Emma Davis', 'emma.davis@example.com', '01067890123', '2024-11-29 16:40:39'),
(12, 'Frank Wilson', 'frank.wilson@example.com', '01078901234', '2024-11-29 16:40:40'),
(13, 'Grace Taylor', 'grace.taylor@example.com', '01089012345', '2024-11-29 16:40:41'),
(14, 'Henry Anderson', 'henry.anderson@example.com', '01090123456', '2024-11-29 16:40:42'),
(15, 'Isabel Martinez', 'isabel.martinez@example.com', '01001234567', '2024-11-29 16:40:43'),
(16, 'Jack Thompson', 'jack.thompson@example.com', '01012345678', '2024-11-29 16:40:44'),
(17, 'Karen White', 'karen.white@example.com', '01023456780', '2024-11-29 16:40:45'),
(18, 'Liam Harris', 'liam.harris@example.com', '01034567891', '2024-11-29 16:40:46'),
(19, 'Mia Clark', 'mia.clark@example.com', '01045678902', '2024-11-29 16:40:47'),
(20, 'Noah Lewis', 'noah.lewis@example.com', '01056789013', '2024-11-29 16:40:48'),
(21, 'Olivia Walker', 'olivia.walker@example.com', '01067890124', '2024-11-29 16:40:49'),
(22, 'Peter Hall', 'peter.hall@example.com', '01078901235', '2024-11-29 16:40:50'),
(23, 'Quinn Adams', 'quinn.adams@example.com', '01089012346', '2024-11-29 16:40:51'),
(24, 'Rachel Green', 'rachel.green@example.com', '01090123457', '2024-11-29 16:40:52'),
(25, 'Samuel Baker', 'samuel.baker@example.com', '01001234568', '2024-11-29 16:40:53'),
(26, 'Tina Evans', 'tina.evans@example.com', '01012345679', '2024-11-29 16:40:54'),
(27, 'Ulysses King', 'ulysses.king@example.com', '01023456781', '2024-11-29 16:40:55'),
(28, 'Victoria Scott', 'victoria.scott@example.com', '01034567892', '2024-11-29 16:40:56'),
(29, 'William Turner', 'william.turner@example.com', '01045678903', '2024-11-29 16:40:57'),
(30, 'Xena Carter', 'xena.carter@example.com', '01056789014', '2024-11-29 16:40:58'),
(31, 'Yannick Ross', 'yannick.ross@example.com', '01067890125', '2024-11-29 16:40:59'),
(32, 'Zoe Mitchell', 'zoe.mitchell@example.com', '01078901236', '2024-11-29 16:41:00'),
(33, 'Adam Nelson', 'adam.nelson@example.com', '01089012347', '2024-11-29 16:41:01'),
(34, 'Bella Cooper', 'bella.cooper@example.com', '01090123458', '2024-11-29 16:41:02'),
(35, 'Charlie Reed', 'charlie.reed@example.com', '01001234569', '2024-11-29 16:41:03'),
(36, 'Diana Wood', 'diana.wood@example.com', '01012345680', '2024-11-29 16:41:04'),
(37, 'Ethan Morgan', 'ethan.morgan@example.com', '01023456782', '2024-11-29 16:41:05'),
(38, 'Fiona Kelly', 'fiona.kelly@example.com', '01034567893', '2024-11-29 16:41:06'),
(39, 'George Foster', 'george.foster@example.com', '01045678904', '2024-11-29 16:41:07'),
(40, 'Hannah Price', 'hannah.price@example.com', '01056789015', '2024-11-29 16:41:08'),
(41, 'Ian Sanders', 'ian.sanders@example.com', '01067890126', '2024-11-29 16:41:09'),
(42, 'Julia Long', 'julia.long@example.com', '01078901237', '2024-11-29 16:41:10'),
(43, 'Kevin Hughes', 'kevin.hughes@example.com', '01089012348', '2024-11-29 16:41:11'),
(44, 'Laura Fisher', 'laura.fisher@example.com', '01090123459', '2024-11-29 16:41:12'),
(45, 'Michael Gray', 'michael.gray@example.com', '01001234570', '2024-11-29 16:41:13'),
(46, 'Natalie Ward', 'natalie.ward@example.com', '01012345681', '2024-11-29 16:41:14'),
(47, 'Oscar Bennett', 'oscar.bennett@example.com', '01023456783', '2024-11-29 16:41:15'),
(48, 'Pamela Cox', 'pamela.cox@example.com', '01034567894', '2024-11-29 16:41:16'),
(49, 'Quentin Howard', 'quentin.howard@example.com', '01045678905', '2024-11-29 16:41:17'),
(50, 'Rose Simpson', 'rose.simpson@example.com', '01056789016', '2024-11-29 16:41:18'),
(51, 'Steven Ellis', 'steven.ellis@example.com', '01067890127', '2024-11-29 16:41:19'),
(52, 'Tara Harrison', 'tara.harrison@example.com', '01078901238', '2024-11-29 16:41:20'),
(53, 'Ursula Gibson', 'ursula.gibson@example.com', '01089012349', '2024-11-29 16:41:21'),
(54, 'Vincent Wallace', 'vincent.wallace@example.com', '01090123460', '2024-11-29 16:41:22'),
(55, 'Wendy Mason', 'wendy.mason@example.com', '01001234571', '2024-11-29 16:41:23'),
(56, 'Xavier Hunt', 'xavier.hunt@example.com', '01012345682', '2024-11-29 16:41:24'),
(57, 'Yvonne Wells', 'yvonne.wells@example.com', '01023456784', '2024-11-29 16:41:25'),
(58, 'Zachary Ford', 'zachary.ford@example.com', '01034567895', '2024-11-29 16:41:26'),
(59, 'Abigail Hart', 'abigail.hart@example.com', '01045678906', '2024-11-29 16:41:27'),
(60, 'Benjamin Cole', 'benjamin.cole@example.com', '01056789017', '2024-11-29 16:41:28'),
(61, 'Chloe Webb', 'chloe.webb@example.com', '01067890128', '2024-11-29 16:41:29'),
(62, 'Daniel Stone', 'daniel.stone@example.com', '01078901239', '2024-11-29 16:41:30'),
(63, 'Ella Hawkins', 'ella.hawkins@example.com', '01089012350', '2024-11-29 16:41:31'),
(64, 'Felix Knight', 'felix.knight@example.com', '01090123461', '2024-11-29 16:41:32'),
(65, 'Gabrielle Dunn', 'gabrielle.dunn@example.com', '01001234572', '2024-11-29 16:41:33'),
(66, 'Hugo Pearson', 'hugo.pearson@example.com', '01012345683', '2024-11-29 16:41:34'),
(67, 'Iris Dean', 'iris.dean@example.com', '01023456785', '2024-11-29 16:41:35'),
(68, 'Jason Parsons', 'jason.parsons@example.com', '01034567896', '2024-11-29 16:41:36'),
(69, 'Kylie Newman', 'kylie.newman@example.com', '01045678907', '2024-11-29 16:41:37'),
(70, 'Leo Chambers', 'leo.chambers@example.com', '01056789018', '2024-11-29 16:41:38'),
(71, 'Megan Dawson', 'megan.dawson@example.com', '01067890129', '2024-11-29 16:41:39'),
(72, 'Nathan Watts', 'nathan.watts@example.com', '01078901240', '2024-11-29 16:41:40'),
(73, 'Olivia Francis', 'olivia.francis@example.com', '01089012351', '2024-11-29 16:41:41'),
(74, 'Paul Jennings', 'paul.jennings@example.com', '01090123462', '2024-11-29 16:41:42'),
(75, 'Quinn Sutton', 'quinn.sutton@example.com', '01001234573', '2024-11-29 16:41:43'),
(76, 'Rebecca Barker', 'rebecca.barker@example.com', '01012345684', '2024-11-29 16:41:44'),
(77, 'Simon Fleming', 'simon.fleming@example.com', '01023456786', '2024-11-29 16:41:45'),
(78, 'Tessa Marsh', 'tessa.marsh@example.com', '01034567897', '2024-11-29 16:41:46'),
(79, 'Ulrich Briggs', 'ulrich.briggs@example.com', '01045678908', '2024-11-29 16:41:47'),
(80, 'Vanessa Horton', 'vanessa.horton@example.com', '01056789019', '2024-11-29 16:41:48'),
(81, 'Wesley Poole', 'wesley.poole@example.com', '01067890130', '2024-11-29 16:41:49'),
(82, 'Xena Lambert', 'xena.lambert@example.com', '01078901241', '2024-11-29 16:41:50'),
(83, 'Yannick Holt', 'yannick.holt@example.com', '01089012352', '2024-11-29 16:41:51'),
(84, 'Zara Mccarthy', 'zara.mccarthy@example.com', '01090123463', '2024-11-29 16:41:52'),
(85, 'Alan Hodges', 'alan.hodges@example.com', '01001234574', '2024-11-29 16:41:53'),
(86, 'Bonnie Robson', 'bonnie.robson@example.com', '01012345685', '2024-11-29 16:41:54'),
(87, 'Cameron Barton', 'cameron.barton@example.com', '01023456787', '2024-11-29 16:41:55'),
(88, 'Daisy Mcdonald', 'daisy.mcdonald@example.com', '01034567898', '2024-11-29 16:41:56'),
(89, 'Evan Thornton', 'evan.thornton@example.com', '01045678909', '2024-11-29 16:41:57'),
(90, 'Faye Walton', 'faye.walton@example.com', '01056789020', '2024-11-29 16:41:58'),
(91, 'Gavin Mckenzie', 'gavin.mckenzie@example.com', '01067890131', '2024-11-29 16:41:59'),
(92, 'Holly Reeves', 'holly.reeves@example.com', '01078901242', '2024-11-29 16:42:00'),
(93, 'Isaac Cooke', 'isaac.cooke@example.com', '01089012353', '2024-11-29 16:42:01'),
(94, 'Jasmine Gibbs', 'jasmine.gibbs@example.com', '01090123464', '2024-11-29 16:42:02'),
(95, 'Keith Goodwin', 'keith.goodwin@example.com', '01001234575', '2024-11-29 16:42:03'),
(96, 'Leah Carpenter', 'leah.carpenter@example.com', '01012345686', '2024-11-29 16:42:04'),
(97, 'Marcus Stephenson', 'marcus.stephenson@example.com', '01023456788', '2024-11-29 16:42:05'),
(98, 'Nina Buckley', 'nina.buckley@example.com', '01034567899', '2024-11-29 16:42:06'),
(99, 'Oscar Watkins', 'oscar.watkins@example.com', '01045678910', '2024-11-29 16:42:07'),
(100, 'Penny Savage', 'penny.savage@example.com', '01056789021', '2024-11-29 16:42:08'),
(101, 'Quinn Griffiths', 'quinn.griffiths@example.com', '01067890132', '2024-11-29 16:42:09'),
(102, 'Ryan Holloway', 'ryan.holloway@example.com', '01078901243', '2024-11-29 16:42:10'),
(103, 'Sophia Frost', 'sophia.frost@example.com', '01089012354', '2024-11-29 16:42:11'),
(104, 'Tyler Mcguire', 'tyler.mcguire@example.com', '01090123465', '2024-11-29 16:42:12'),
(105, 'Uma Whitehead', 'uma.whitehead@example.com', '01001234576', '2024-11-29 16:42:13'),
(106, 'Victor Slater', 'victor.slater@example.com', '01012345687', '2024-11-29 16:42:14'),
(107, 'Willow Hendricks', 'willow.hendricks@example.com', '01023456789', '2024-11-29 16:42:15');



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