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
-- Database: `patient`
--
CREATE DATABASE IF NOT EXISTS `subsidy` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `subsidy`;

-- --------------------------------------------------------

--
-- Table structure for table `patient`
--

DROP TABLE IF EXISTS `subsidy`;
CREATE TABLE IF NOT EXISTS `subsidy` (
  `nric` varchar(9) NOT NULL,
  `cardNumber` varchar(64) NOT NULL,
  `cardType` char(128) NOT NULL,
  `organisationType` char(64) NULL,
  `expiryDate` varchar(10) NOT NULL,
  PRIMARY KEY (`cardNumber`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `patient`
--

INSERT INTO `subsidy` (`nric`, `cardNumber`, `cardType`, `organisationType`, `expiryDate`) VALUES
('S9812381D', '11237623', 'GreenCHAS', NULL, '2019-03-29'),
('S9812382B', '78045522', 'Merdeka', NULL, '2020-09-05'),
('S9812385G', '01148732', 'BlueCHAS', NULL, '2023-12-15'),
('G1612350T', '90348226', 'Pioneer', NULL, '2025-01-26'),
('F1612347K', '55230598', 'Company', 'DBS', '2022-07-08');
COMMIT;