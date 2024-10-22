-- MySQL dump 10.13  Distrib 8.0.39, for Win64 (x86_64)
--
-- Host: localhost    Database: icms
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alerts`
--

DROP TABLE IF EXISTS `alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alerts` (
  `alert_id` int NOT NULL AUTO_INCREMENT,
  `product_id` int DEFAULT NULL,
  `alert_type` varchar(255) DEFAULT NULL,
  `alert_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`alert_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `alerts_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alerts`
--

LOCK TABLES `alerts` WRITE;
/*!40000 ALTER TABLE `alerts` DISABLE KEYS */;
/*!40000 ALTER TABLE `alerts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory`
--

DROP TABLE IF EXISTS `inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventory` (
  `inventory_id` int NOT NULL,
  `product_id` int DEFAULT NULL,
  `quantity` int DEFAULT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`inventory_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `inventory_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory`
--

LOCK TABLES `inventory` WRITE;
/*!40000 ALTER TABLE `inventory` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `order_id` int NOT NULL,
  `product_id` int DEFAULT NULL,
  `product_name` varchar(225) DEFAULT NULL,
  `customer_name` varchar(255) DEFAULT NULL,
  `customer_address` varchar(255) DEFAULT NULL,
  `order_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `expected_delivery_date` timestamp NULL DEFAULT NULL,
  `quantity` int DEFAULT NULL,
  `total_amount` decimal(10,2) DEFAULT NULL,
  `status` enum('processing','confirmed','shipped','delivered') NOT NULL,
  PRIMARY KEY (`order_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1001,20915,'Mouse','John Doe','123 Elm Street','2024-01-01 05:00:00','2024-01-05 05:00:00',2,70.00,'confirmed'),(1002,20916,'Keyboard','Jane Smith','456 Maple Avenue','2024-01-03 03:30:00','2024-01-07 03:30:00',1,60.00,'processing'),(1003,20917,'Monitor','Michael Brown','789 Oak Drive','2024-01-05 05:30:00','2024-01-10 05:30:00',1,200.00,'shipped'),(1004,20918,'Laptop','David Johnson','101 Pine Road','2024-01-10 09:00:00','2024-01-15 09:00:00',1,1200.00,'delivered'),(1005,20919,'Graphics Card','Emily Davis','202 Birch Boulevard','2024-01-12 03:15:00','2024-01-18 03:15:00',1,500.00,'shipped'),(1006,20920,'SSD','Matthew Wilson','303 Cedar Lane','2024-01-15 10:30:00','2024-01-20 10:30:00',2,300.00,'confirmed'),(1007,20921,'Headphones','Sophia Martinez','404 Spruce Circle','2024-01-20 04:45:00','2024-01-25 04:45:00',1,80.00,'processing'),(1008,20922,'Webcam','Daniel Garcia','505 Redwood Court','2024-01-22 07:30:00','2024-01-27 07:30:00',3,120.00,'confirmed'),(1009,20923,'Charger','Isabella Hernandez','606 Sequoia Street','2024-01-24 04:00:00','2024-01-29 04:00:00',2,50.00,'delivered'),(1010,20924,'Smartphone','James White','707 Poplar Avenue','2024-01-28 07:15:00','2024-02-02 07:15:00',1,800.00,'shipped'),(1011,20925,'Tablet','Mia Thomas','808 Magnolia Drive','2024-02-01 08:30:00','2024-02-06 08:30:00',1,300.00,'confirmed'),(1012,20926,'Power Bank','Olivia Lewis','909 Fir Place','2024-02-05 04:30:00','2024-02-10 04:30:00',3,135.00,'processing'),(1013,20927,'Mouse Pad','Liam Lee','1010 Palm Way','2024-02-07 04:00:00','2024-02-12 04:00:00',5,75.00,'shipped'),(1014,20928,'Speaker','Emma Walker','1111 Walnut Road','2024-02-10 10:15:00','2024-02-15 10:15:00',2,120.00,'delivered'),(1015,20929,'Camera','Ethan Young','1212 Maplewood Drive','2024-02-12 05:30:00','2024-02-17 05:30:00',1,900.00,'processing'),(1016,20930,'Smartwatch','Charlotte Hall','1313 Birchwood Avenue','2024-02-15 02:45:00','2024-02-20 02:45:00',1,150.00,'shipped'),(1017,20931,'Printer','Mason King','1414 Redwood Avenue','2024-02-18 08:00:00','2024-02-23 08:00:00',1,180.00,'confirmed'),(1018,20932,'Router','Amelia Scott','1515 Cedarwood Lane','2024-02-20 11:30:00','2024-02-25 11:30:00',1,120.00,'shipped'),(1019,20933,'Microphone','Benjamin Harris','1616 Ash Drive','2024-02-22 07:00:00','2024-02-27 07:00:00',1,50.00,'confirmed'),(1020,20934,'External Hard Drive','Harper Adams','1717 Redwood Court','2024-02-25 03:30:00','2024-03-02 03:30:00',2,200.00,'delivered'),(1021,20915,'Mouse','Alexander Gray','1818 Pine Road','2024-09-01 04:30:00','2024-09-05 04:30:00',1,35.00,'confirmed'),(1022,20916,'Keyboard','Ava Lee','1919 Maple Avenue','2024-09-02 05:30:00','2024-09-07 05:30:00',1,60.00,'processing'),(1023,20917,'Monitor','Elijah Patel','2020 Birch Boulevard','2024-09-03 06:30:00','2024-09-08 06:30:00',1,200.00,'shipped'),(1024,20918,'Laptop','Lily Tran','2121 Cedar Lane','2024-09-04 07:30:00','2024-09-09 07:30:00',1,1200.00,'confirmed'),(1025,20919,'Graphics Card','Noah Kim','2222 Redwood Court','2024-09-05 08:30:00','2024-09-10 08:30:00',1,500.00,'processing'),(1026,20920,'SSD','Sophia Rodriguez','2323 Spruce Circle','2024-09-06 09:30:00','2024-09-11 09:30:00',2,300.00,'shipped'),(1027,20921,'Headphones','Mason Brown','2424 Sequoia Street','2024-09-07 10:30:00','2024-09-12 10:30:00',1,80.00,'confirmed'),(1028,20922,'Webcam','Emma Taylor','2525 Poplar Avenue','2024-09-08 11:30:00','2024-09-13 11:30:00',3,120.00,'processing'),(1029,20923,'Charger','Oliver White','2626 Magnolia Drive','2024-09-09 12:30:00','2024-09-14 12:30:00',2,50.00,'shipped'),(1030,20924,'Smartphone','Ava Martin','2727 Walnut Road','2024-09-10 13:30:00','2024-09-15 13:30:00',1,800.00,'confirmed');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `product_id` int NOT NULL,
  `product_name` varchar(255) NOT NULL,
  `product_description` text,
  `price` decimal(10,2) DEFAULT NULL,
  `quantity` int DEFAULT NULL,
  `date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (20915,'Mouse','High quality',35.00,200,'2023-12-31 18:30:00'),(20916,'Keyboard','Mechanical keyboard',60.00,150,'2024-02-09 18:30:00'),(20917,'Monitor','27-inch LED monitor',200.00,80,'2024-03-04 18:30:00'),(20918,'Laptop','Gaming laptop',1200.00,50,'2024-04-14 18:30:00'),(20919,'Graphics Card','NVIDIA RTX 3060',500.00,30,'2024-05-21 18:30:00'),(20920,'SSD','1TB NVMe SSD',150.00,100,'2024-05-31 18:30:00'),(20921,'Headphones','Noise-canceling headphones',80.00,60,'2024-07-09 18:30:00'),(20922,'Webcam','HD Webcam',40.00,90,'2024-08-04 18:30:00'),(20923,'Charger','65W USB-C Charger',25.00,200,'2024-09-11 18:30:00'),(20924,'Smartphone','Latest model smartphone',800.00,40,'2024-10-19 18:30:00'),(20925,'Tablet','10-inch tablet',300.00,70,'2024-11-10 18:30:00'),(20926,'Power Bank','20,000mAh power bank',45.00,120,'2024-01-14 18:30:00'),(20927,'Mouse Pad','Extended mouse pad',15.00,200,'2024-02-17 18:30:00'),(20928,'Speaker','Bluetooth speaker',60.00,100,'2024-03-19 18:30:00'),(20929,'Camera','DSLR camera',900.00,30,'2024-04-24 18:30:00'),(20930,'Smartwatch','Fitness tracking smartwatch',150.00,85,'2024-05-29 18:30:00'),(20931,'Printer','All-in-one printer',180.00,40,'2024-06-21 18:30:00'),(20932,'Router','Wi-Fi 6 router',120.00,70,'2024-07-17 18:30:00'),(20933,'Microphone','USB microphone',50.00,95,'2024-08-13 18:30:00'),(20934,'External Hard Drive','2TB external hard drive',100.00,110,'2024-09-24 18:30:00');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `supplierorders`
--

DROP TABLE IF EXISTS `supplierorders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `supplierorders` (
  `supplier_order_id` int NOT NULL,
  `supplier_id` int DEFAULT NULL,
  `supplier_name` varchar(255) NOT NULL,
  `product_name` varchar(255) NOT NULL,
  `order_count` int NOT NULL,
  `order_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `expected_delivery_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('pending','delivered') DEFAULT NULL,
  `total_amount` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`supplier_order_id`),
  KEY `supplier_id` (`supplier_id`),
  CONSTRAINT `supplierorders_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`supplier_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `supplierorders`
--

LOCK TABLES `supplierorders` WRITE;
/*!40000 ALTER TABLE `supplierorders` DISABLE KEYS */;
INSERT INTO `supplierorders` VALUES (1,15986,'Alpha Supplies','Product A',50,'2024-08-01 04:30:00','2024-08-05 04:30:00','pending',2500.00),(2,15987,'Beta Traders','Product B',30,'2024-08-02 05:30:00','2024-08-07 05:30:00','delivered',1200.00),(3,15988,'Gamma Goods','Product C',20,'2024-08-03 06:30:00','2024-08-08 06:30:00','pending',800.00),(4,15989,'Delta Imports','Product D',15,'2024-08-04 07:30:00','2024-08-09 07:30:00','delivered',375.00),(5,15990,'Epsilon Exports','Product E',40,'2024-08-05 08:30:00','2024-08-10 08:30:00','pending',2000.00),(6,15991,'Zeta Ventures','Product F',25,'2024-08-06 09:30:00','2024-08-11 09:30:00','delivered',875.00),(7,15992,'Eta Enterprises','Product G',35,'2024-08-07 10:30:00','2024-08-12 10:30:00','pending',1400.00),(8,15993,'Theta Traders','Product H',60,'2024-08-08 11:30:00','2024-08-13 11:30:00','delivered',3600.00),(9,15994,'Iota Solutions','Product I',45,'2024-08-09 12:30:00','2024-08-14 12:30:00','pending',1800.00),(10,15995,'Kappa Products','Product J',55,'2024-08-10 13:30:00','2024-08-15 13:30:00','delivered',2750.00),(11,15996,'Lambda Labs','Product A',30,'2024-08-11 14:30:00','2024-08-16 14:30:00','pending',1500.00),(12,15997,'Mu Manufacturing','Product B',25,'2024-08-12 15:30:00','2024-08-17 15:30:00','delivered',1000.00),(13,15998,'Nu Network','Product C',20,'2024-08-13 16:30:00','2024-08-18 16:30:00','pending',800.00),(14,15999,'Xi Xpress','Product D',40,'2024-08-14 17:30:00','2024-08-19 17:30:00','delivered',1600.00),(15,16000,'Omicron Imports','Product E',50,'2024-08-14 18:30:00','2024-08-19 18:30:00','pending',2500.00),(16,15986,'Alpha Supplies','Product K',20,'2024-09-01 04:30:00','2024-09-05 04:30:00','pending',1000.00),(17,15987,'Beta Traders','Product L',30,'2024-09-02 05:30:00','2024-09-07 05:30:00','delivered',1500.00),(18,15988,'Gamma Goods','Product M',40,'2024-09-03 06:30:00','2024-09-08 06:30:00','pending',2000.00),(19,15989,'Delta Imports','Product N',50,'2024-09-04 07:30:00','2024-09-09 07:30:00','delivered',2500.00),(20,15990,'Epsilon Exports','Product O',25,'2024-09-05 08:30:00','2024-09-10 08:30:00','pending',1250.00),(21,15991,'Zeta Ventures','Product P',35,'2024-09-06 09:30:00','2024-09-11 09:30:00','delivered',1750.00),(22,15992,'Eta Enterprises','Product Q',45,'2024-09-07 10:30:00','2024-09-12 10:30:00','pending',2250.00),(23,15993,'Theta Traders','Product R',55,'2024-09-08 11:30:00','2024-09-13 11:30:00','delivered',2750.00),(24,15994,'Iota Solutions','Product S',20,'2024-09-09 12:30:00','2024-09-14 12:30:00','pending',1000.00),(25,15995,'Kappa Products','Product T',30,'2024-09-10 13:30:00','2024-09-15 13:30:00','delivered',1500.00);
/*!40000 ALTER TABLE `supplierorders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suppliers`
--

DROP TABLE IF EXISTS `suppliers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suppliers` (
  `supplier_id` int NOT NULL,
  `supplier_name` varchar(255) NOT NULL,
  `product_count` int NOT NULL,
  `contact_phone` varchar(255) DEFAULT NULL,
  `contact_email` varchar(255) DEFAULT NULL,
  `performance` enum('High','Medium','Low') DEFAULT NULL,
  `avg_lead_time` int DEFAULT NULL,
  `status` enum('Active','Inactive') DEFAULT NULL,
  PRIMARY KEY (`supplier_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suppliers`
--

LOCK TABLES `suppliers` WRITE;
/*!40000 ALTER TABLE `suppliers` DISABLE KEYS */;
INSERT INTO `suppliers` VALUES (15986,'Alpha Supplies',50,'123-456-7890','contact@alphasupplies.com','High',10,'Active'),(15987,'Beta Traders',30,'234-567-8901','info@betatraders.com','Medium',15,'Active'),(15988,'Gamma Goods',40,'345-678-9012','support@gammagoods.com','High',12,'Inactive'),(15989,'Delta Imports',20,'456-789-0123','sales@deltaimports.com','Low',20,'Active'),(15990,'Epsilon Exports',35,'567-890-1234','service@epsilonexports.com','Medium',18,'Active'),(15991,'Zeta Ventures',25,'678-901-2345','contact@zetaventures.com','High',14,'Inactive'),(15992,'Eta Enterprises',45,'789-012-3456','info@etaenterprises.com','Medium',16,'Active'),(15993,'Theta Traders',55,'890-123-4567','support@thetatraders.com','Low',22,'Active'),(15994,'Iota Solutions',60,'901-234-5678','sales@iotasolutions.com','High',11,'Active'),(15995,'Kappa Products',15,'012-345-6789','service@kappaproducts.com','Medium',19,'Inactive'),(15996,'Lambda Labs',70,'123-456-7891','contact@lambdalabs.com','High',13,'Active'),(15997,'Mu Manufacturing',25,'234-567-8902','info@mumfg.com','Medium',17,'Active'),(15998,'Nu Network',30,'345-678-9013','support@nunetwork.com','Low',21,'Inactive'),(15999,'Xi Xpress',40,'456-789-0124','sales@xixpress.com','High',10,'Active'),(16000,'Omicron Imports',50,'567-890-1235','service@omicronimports.com','Medium',15,'Active');
/*!40000 ALTER TABLE `suppliers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transactions` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL,
  `transaction_type` enum('IN','OUT') NOT NULL,
  `transaction_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `total_amount` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`transaction_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactions`
--

LOCK TABLES `transactions` WRITE;
/*!40000 ALTER TABLE `transactions` DISABLE KEYS */;
INSERT INTO `transactions` VALUES (1,20915,2,'IN','2024-01-05 04:30:00',70.00),(2,20916,1,'OUT','2024-01-10 05:30:00',60.00),(3,20917,1,'IN','2024-01-15 06:30:00',200.00),(4,20918,1,'OUT','2024-01-20 07:30:00',1200.00),(5,20919,1,'IN','2024-01-25 08:30:00',500.00),(6,20920,2,'OUT','2024-02-01 09:30:00',300.00),(7,20921,1,'IN','2024-02-05 10:30:00',80.00),(8,20922,3,'OUT','2024-02-10 11:30:00',120.00),(9,20923,2,'IN','2024-02-15 12:30:00',50.00),(10,20924,1,'OUT','2024-02-20 13:30:00',800.00),(11,20915,2,'IN','2024-03-01 04:30:00',70.00),(12,20916,1,'OUT','2024-03-05 05:30:00',60.00),(13,20917,1,'IN','2024-03-10 06:30:00',200.00),(14,20918,1,'OUT','2024-03-15 07:30:00',1200.00),(15,20919,1,'IN','2024-03-20 08:30:00',500.00),(16,20920,2,'OUT','2024-03-25 09:30:00',300.00),(17,20921,1,'IN','2024-04-01 10:30:00',80.00),(18,20922,3,'OUT','2024-04-05 11:30:00',120.00),(19,20923,2,'IN','2024-04-10 12:30:00',50.00),(20,20924,1,'OUT','2024-04-15 13:30:00',800.00),(21,20915,2,'IN','2024-05-01 04:30:00',70.00),(22,20916,1,'OUT','2024-05-05 05:30:00',60.00),(23,20917,1,'IN','2024-05-10 06:30:00',200.00),(24,20918,1,'OUT','2024-05-15 07:30:00',1200.00),(25,20919,1,'IN','2024-05-20 08:30:00',500.00),(26,20920,2,'OUT','2024-05-25 09:30:00',300.00),(27,20921,1,'IN','2024-06-01 10:30:00',80.00),(28,20922,3,'OUT','2024-06-05 11:30:00',120.00),(29,20923,2,'IN','2024-06-10 12:30:00',50.00),(30,20924,1,'OUT','2024-06-15 13:30:00',800.00),(31,20915,2,'IN','2024-07-01 04:30:00',70.00),(32,20916,1,'OUT','2024-07-05 05:30:00',60.00),(33,20917,1,'IN','2024-07-10 06:30:00',200.00),(34,20918,1,'OUT','2024-07-15 07:30:00',1200.00),(35,20919,1,'IN','2024-07-20 08:30:00',500.00),(36,20920,2,'OUT','2024-07-25 09:30:00',300.00),(37,20921,1,'IN','2024-08-01 10:30:00',80.00),(38,20922,3,'OUT','2024-08-05 11:30:00',120.00),(39,20923,2,'IN','2024-08-10 12:30:00',50.00),(40,20924,1,'OUT','2024-08-15 13:30:00',800.00),(41,20915,2,'IN','2024-09-01 04:30:00',70.00),(42,20916,1,'OUT','2024-09-05 05:30:00',60.00),(43,20917,1,'IN','2024-09-10 06:30:00',200.00),(44,20918,1,'OUT','2024-09-12 07:30:00',1200.00),(45,20919,1,'IN','2024-09-13 08:30:00',500.00);
/*!40000 ALTER TABLE `transactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'user@example.com','user','securepassword');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-10-22 11:14:19
