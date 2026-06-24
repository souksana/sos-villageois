-- MySQL dump 10.13  Distrib 9.6.0, for macos14.8 (x86_64)
--
-- Host: localhost    Database: sos_villageois
-- ------------------------------------------------------
-- Server version	9.6.0

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
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '1420e6c6-5fe4-11f1-a7ab-cb5e7636a9ad:1-340';

--
-- Dumping data for table `activite`
--

LOCK TABLES `activite` WRITE;
/*!40000 ALTER TABLE `activite` DISABLE KEYS */;
/*!40000 ALTER TABLE `activite` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `annonce`
--

LOCK TABLES `annonce` WRITE;
/*!40000 ALTER TABLE `annonce` DISABLE KEYS */;
INSERT INTO `annonce` VALUES (1,'arroser mes fleurs','svp besoin d\'aide j\'ai mal au dos pour mes fleurs ! #help','jardinage','2026-06-24 00:52:42','ouverte',2),(2,'repeindre ma porte','j\'ai acheté la peinture mais je sais pas peindre...','bricolage','2026-06-24 00:53:34','ouverte',2),(3,'ville de merde!!','qui pour me louer un camion de déménagement j\'en peux plus de cette ville','déménagement','2026-06-24 00:54:35','ouverte',5),(4,'Promener Orphée','Je suis blessée et je ne peux plus promener mon chien.','garde d\'animaux','2026-06-24 00:55:53','ouverte',4),(5,'recherche chef privé','salut tout le monde je cherche quelqu\'un pour faire mes gamelles pour le midi (je vais à la salle)','cuisine','2026-06-24 00:57:18','ouverte',3),(6,'Je cherche un sexfriend','Miam miam le gros chibrax','autre','2026-06-24 09:34:05','ouverte',6),(7,'sortir kirkri','besoin d\'aide pour sortir mon adorable petit animal troooop mignon','garde d\'animaux','2026-06-24 10:31:07','ouverte',8),(8,'besoin d\'aide pour reviser les maths','au secours','autre','2026-06-24 11:45:25','ouverte',1);
/*!40000 ALTER TABLE `annonce` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `commentaire`
--

LOCK TABLES `commentaire` WRITE;
/*!40000 ALTER TABLE `commentaire` DISABLE KEYS */;
INSERT INTO `commentaire` VALUES (1,'pas moi dsl','2026-06-24 12:08:02',8,8);
/*!40000 ALTER TABLE `commentaire` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `disponibilite`
--

LOCK TABLES `disponibilite` WRITE;
/*!40000 ALTER TABLE `disponibilite` DISABLE KEYS */;
/*!40000 ALTER TABLE `disponibilite` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `interet`
--

LOCK TABLES `interet` WRITE;
/*!40000 ALTER TABLE `interet` DISABLE KEYS */;
/*!40000 ALTER TABLE `interet` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `proposition`
--

LOCK TABLES `proposition` WRITE;
/*!40000 ALTER TABLE `proposition` DISABLE KEYS */;
/*!40000 ALTER TABLE `proposition` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `Reagir`
--

LOCK TABLES `Reagir` WRITE;
/*!40000 ALTER TABLE `Reagir` DISABLE KEYS */;
INSERT INTO `Reagir` VALUES (8,5,'urgence'),(1,8,'coeur'),(1,8,'rire'),(1,8,'urgence'),(8,8,'coeur'),(8,8,'pouce'),(8,8,'rire'),(8,8,'urgence');
/*!40000 ALTER TABLE `Reagir` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `utilisateur`
--

LOCK TABLES `utilisateur` WRITE;
/*!40000 ALTER TABLE `utilisateur` DISABLE KEYS */;
INSERT INTO `utilisateur` VALUES (1,'admin','admin@sos.fr','scrypt:32768:8:1$9WnKvQQv2SRlAaZp$bd611c858c318bef311aec849e5948ce4bc59b27e05709ee09f1fffca9688fe42f5b994adb3a898ce66963bc6a598b24bac7598e6c6e8d32faac35129d307f09','admin','Tom Nook',''),(2,'souksana','test@sos.fr','scrypt:32768:8:1$hQlQLNgMKGAe54T7$ccda04c75976f1163f0e99aaebd19b4959dd9653c5405e60bad92da56b0a21dc6f2d77afd30c8f5b7273624d5c38ad3177a343c988ad393aa27961ebb18a641a','user','Isabelle',''),(3,'zio','admin2@sos.fr','scrypt:32768:8:1$ZMxg5a8ypopAJwxW$08d4cd05c0ecdd494df241a6eb52e3c71ae7f4df39e840b1dc63a8035d5930dd85ac26d37e27737ed7d94a94922ced91495bf63f19e1c07ca1b3149814de4c66','admin','Follet',''),(4,'maud','maud@sos.fr','scrypt:32768:8:1$P7GszntRhUqFvvlp$43196e73cc9d6a3811210dacabacf38d80507b4d6518b8a4de05dcaec0458cbe9491e2420fdac37db25f88c4d411f9afea75c163261a18af4cb22027f6e90288','user','Marshal',''),(5,'prisca','prisca@sos.fr','scrypt:32768:8:1$yDEqit9k8WHReVIa$6e76d3c68e154ffc63bdf493ab995cbd2e0eb2305974d75f1b8cfc3e1cab21b2190cc616392c54fbba1adf20febfff6891389f6a68550fd91d65d17846a0d406','user','Raymond',''),(6,'Gu','gugulugugu@gmail.com','scrypt:32768:8:1$pWjhKyRRcLoXcCx9$391968113dc97086a3c9f2fea34200a2c67cfdfc7f9fe20c55e2f471740593acb0438fb02c4bf8bcdb5278c0daa3b3ab4464f24dcf85ae6f926924b80a2870cc','user','Admiral','https://dodo.ac/np/images/0/0a/Admiral%27s_Photo_NH_Texture.png'),(7,'juju','blabla@gmail.com','scrypt:32768:8:1$AJfcxDb39qvRkyDy$444f18bc75f2564a28e9c108867879edc48ef85d6fedfdc190d96dd67270a1c2a6c056d7f9a214d8a54408e4c0e761019ee6068bae3b779dddfa615d7137f74b','user','Alfonso','https://dodo.ac/np/images/e/e8/Alfonso%27s_Photo_NH_Texture.png'),(8,'yugyeomiste','fofof@gmail.com','scrypt:32768:8:1$CqTpkOUPldP8DvYP$15db2bfe3674152b8d52ae6b8fd0843ab134d17290610c54be8c3e3a07fe5deacc9adbe3a89f979b244a0ad1ff6c5f7462c7a8895800bf072536feec88f54e9f','user','Bunnie','https://dodo.ac/np/images/f/f9/Bunnie%27s_Photo_NH_Texture.png');
/*!40000 ALTER TABLE `utilisateur` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-24 12:46:06
