-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306


SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `patientRecord`
--
CREATE DATABASE IF NOT EXISTS `patientRecord` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `patientRecord`;

-- --------------------------------------------------------

--
-- Table structure for table `patientRecord`
--

DROP TABLE IF EXISTS `patientRecord`;
CREATE TABLE IF NOT EXISTS `patientRecord` (
  `patientRecordId` int(11) AUTO_INCREMENT NOT NULL,
  `nric` varchar(9) NOT NULL,
  `clinicId` int(3) NOT NULL, 
  `drugName` varchar(128) NOT NULL,
  `prescribeQuantity` int(11) NOT NULL,
  `date` varchar(64) NOT NULL,
  `time` varchar(64) NOT NULL,
  PRIMARY KEY (`patientRecordId`,`nric`,`clinicId`,`drugName`,`date`,`time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `patientRecord`
--

INSERT INTO `patientRecord` (`nric`,`clinicId`,`drugName`,`prescribeQuantity`,`date`,`time`) VALUES
('S9245177A',7, 'Tamoxifen', 20, '2022-01-11', '16:15:00'),
('S9640091H',8, 'Diazepam', 15, '2022-01-12', '13:30:00'),
('S9812379B',2,'Baricitinib', 20,'2022-01-19', '09:00:00'),
('S9812379B',2,'Hydrocortisone', 1,'2022-01-19', '09:01:00'),
('S9812388A',8, 'Etravirine', 10, '2022-01-19', '14:45:00'),
('S9812388A',1,'Paracetamol', 20, '2022-01-27','13:30:00'),
('S9812388A',1,'Vitamin A', 25, '2022-01-27','13:31:00'),
('S9640091H',4,'Calcium Acetate', 20,'2022-02-01', '14:30:00'),
('S9640091H',4,'Sodium Bicarbonate', 15,'2022-02-01', '14:31:00'),
('S9245177A',6, 'Fludrocortisone Acetate', 30,'2022-02-07', '13:00:00'),
('S9245177A',6, 'Vitamin A', 30,'2022-02-07', '13:01:00'),
('S9812379B',7, 'Warfarin Sodium', 30, '2022-02-09', '09:45:00'),
('S7380725E',2, 'Gliclazide', 30, '2022-02-11', '16:30:00'),
('S7380725E',6, 'Rifampicin', 10,'2022-02-14', '10:45:00'),
('S7955237B',3, 'Nitrazepam', 20, '2022-02-17', '15:00:00'),
('S7955237B',3, 'Baricitinib',15, '2022-02-17', '15:01:00'),
('S8243452F',4,'Ursodeoxycholic Acid', 20,'2022-02-19', '16:35:00'),
('S9812388A',3, 'Nitrazepam', 20, '2022-02-25', '15:30:00'),
('S8243452F',1, 'Zidovudine', 30, '2022-02-27', '16:00:00'),
('S8243452F',1, 'Ibuprofen', 30,'2022-02-27', '16:01:00'),
('S8243452F',1, 'Etravirine', 30, '2022-02-27', '16:02:00'),
('S7380725E',1, 'Methoxsalen', 30, '2022-02-28', '09:00:00'),
('S7380725E',1, 'Hydrocortisone', 2, '2022-02-28', '09:01:00'),
('S9912375C',7, 'Zidovudine', 5, '2022-03-04', '09:50:00'),
('S9912375C',8, 'Ibuprofen', 10, '2022-03-07', '10:45:00'),
('S9912375C',5, 'Hydrocortisone', 1,'2022-03-12', '09:00:00'),
('S9912375C',5, 'Olanzapine', 10,'2022-03-12', '09:30:00'),
('S9245177A',9, 'Ketoprofen', 20, '2022-03-23', '15:30:00'),
('S9812379B',9, 'Lidocaine', 5, '2022-03-24', '09:45:00'),
('S7955237B',5, 'Quetiapine', 15,'2022-03-24', '10:00:00'),
('S9640091H',9, 'Albendazole', 15, '2022-03-26', '14:45:00')
;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
