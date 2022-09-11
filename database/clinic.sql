-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306


SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+08:00";

--
-- Database: `clinic`
--
CREATE DATABASE IF NOT EXISTS `clinic` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `clinic`;

-- --------------------------------------------------------

--
-- Table structure for table `clinic`
--

DROP TABLE IF EXISTS `clinic`;
CREATE TABLE IF NOT EXISTS `clinic` (
  `clinicId` int(3) NOT NULL, 
  `clinicName` varchar(128) NOT NULL,
  `address` varchar(128) NOT NULL,
  `postalCode` varchar(6) NOT NULL,
  `email` varchar(128) NOT NULL,
  `password` varchar(128) NOT NULL,
  PRIMARY KEY (`clinicId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `clinic`
--

INSERT INTO `clinic` (`clinicId`,`clinicName`,`address`, `postalCode`, `email`,`password`) VALUES
(1, 'Raffles Medical Anchorvale', '370 Alexandra Road #B1-41 Anchorpoint', '159953', 'bryan.shing.2020@scis.smu.edu.sg','one'), 
(2, 'Raffles Medical Ang Mo Kio', 'Blk 722 Ang Mo Kio Avenue 8 #01-2825', '560722', 'bryan.shing.2020@scis.smu.edu.sg','two'), 
(3, 'Raffles Medical Anson Centre', '51 Anson Road, #01-51 Anson Centre', '079904', 'bryan.shing.2020@scis.smu.edu.sg','three'), 
(4, 'Raffles Medical Bishan', 'Blk 283 Bishan Street 22, #01-177', '570283', 'bryan.shing.2020@scis.smu.edu.sg','four'), 
(5, 'Raffles Medical Compass One', '1 Sengkang Square, #04-09, Compass One', '545078', 'bryan.shing.2020@scis.smu.edu.sg','five'), 
(6, 'Raffles Medical Rivervale Mall', '11, Rivervale Crescent, #02-17 Rivervale Mall', '545082', 'bryan.shing.2020@scis.smu.edu.sg','six'), 
(7, 'Raffles Medical Toa Payoh', 'Blk 177 Toa Payoh Central, #01-170', '310177', 'bryan.shing.2020@scis.smu.edu.sg','seven'), 
(8, 'Raffles Medical Hillion Mall', '17 Petir Road, Hillion Mall, #02-07', '678278', 'bryan.shing.2020@scis.smu.edu.sg','eight'),
(9, 'Raffles Medical Tampines 1', '10 Tampines Central 1, #03-28', '529536', 'bryan.shing.2020@scis.smu.edu.sg','nine')
;
COMMIT;