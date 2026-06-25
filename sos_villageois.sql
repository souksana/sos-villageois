-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : jeu. 25 juin 2026 à 11:08
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `sos_villageois`
--

-- --------------------------------------------------------

--
-- Structure de la table `activite`
--

CREATE TABLE `activite` (
  `id_activite` int(11) NOT NULL,
  `nom` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `annonce`
--

CREATE TABLE `annonce` (
  `id_annonce` int(11) NOT NULL,
  `titre` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `tache` varchar(100) DEFAULT NULL,
  `date_creation` datetime DEFAULT current_timestamp(),
  `statut` varchar(20) DEFAULT 'ouverte',
  `id_user` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `annonce`
--

INSERT INTO `annonce` (`id_annonce`, `titre`, `description`, `tache`, `date_creation`, `statut`, `id_user`) VALUES
(1, 'arroser mes fleurs', 'svp besoin d\'aide j\'ai mal au dos pour mes fleurs ! #help', 'jardinage', '2026-06-24 00:52:42', 'ouverte', 2),
(2, 'repeindre ma porte', 'j\'ai acheté la peinture mais je sais pas peindre...', 'bricolage', '2026-06-24 00:53:34', 'ouverte', 2),
(3, 'ville de merde!!', 'qui pour me louer un camion de déménagement j\'en peux plus de cette ville', 'déménagement', '2026-06-24 00:54:35', 'ouverte', 5),
(4, 'Promener Orphée', 'Je suis blessée et je ne peux plus promener mon chien.', 'garde d\'animaux', '2026-06-24 00:55:53', 'ouverte', 4),
(5, 'recherche chef privé', 'salut tout le monde je cherche quelqu\'un pour faire mes gamelles pour le midi (je vais à la salle)', 'cuisine', '2026-06-24 00:57:18', 'ouverte', 3),
(6, 'Je cherche un sexfriend', 'Miam miam le gros chibrax', 'autre', '2026-06-24 09:34:05', 'ouverte', 6),
(7, 'sortir kirkri', 'besoin d\'aide pour sortir mon adorable petit animal troooop mignon', 'garde d\'animaux', '2026-06-24 10:31:07', 'ouverte', 8),
(8, 'besoin d\'aide pour reviser les maths', 'au secours', 'autre', '2026-06-24 11:45:25', 'ouverte', 1),
(9, 'aide pour les courses', 'qui peut me porter 6 packs d\'eau jusqu\'à chez moi svp', 'courses', '2026-06-24 19:34:05', 'ouverte', 9),
(10, 'besoin d\'aide pour ticketmaster', 'svpppp qui veut se connecter avec moi pour avoir + de chance d\'avoir des places pour la rvfleuse', 'informatique', '2026-06-25 09:47:44', 'ouverte', 12),
(11, 'boss genshin', 'qui pour battre signora avec moi j\'en ai marre !!!!!!!!!!', 'informatique', '2026-06-25 10:01:47', 'ouverte', 13),
(12, 'Vacances sans mon lapin', 'je pars en vacs sans mon petit amour, qui est disponible du 30/06 au 02/07 ? :(', 'garde d\'animaux', '2026-06-25 10:08:08', 'ouverte', 14);

-- --------------------------------------------------------

--
-- Structure de la table `commentaire`
--

CREATE TABLE `commentaire` (
  `id_com` int(11) NOT NULL,
  `contenu` text NOT NULL,
  `date_com` datetime DEFAULT current_timestamp(),
  `id_user` int(11) NOT NULL,
  `id_annonce` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `commentaire`
--

INSERT INTO `commentaire` (`id_com`, `contenu`, `date_com`, `id_user`, `id_annonce`) VALUES
(1, 'pas moi dsl', '2026-06-24 12:08:02', 8, 8),
(2, 'courage on est pas ensemble', '2026-06-24 19:33:08', 9, 8),
(3, 'JE SUIS COACH', '2026-06-25 09:43:06', 11, 8),
(4, 'moi!', '2026-06-25 10:02:06', 13, 10);

-- --------------------------------------------------------

--
-- Structure de la table `disponibilite`
--

CREATE TABLE `disponibilite` (
  `id_dispo` int(11) NOT NULL,
  `creneau` varchar(100) DEFAULT NULL,
  `date_dispo` date DEFAULT NULL,
  `description` text DEFAULT NULL,
  `id_user` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `disponibilite`
--

INSERT INTO `disponibilite` (`id_dispo`, `creneau`, `date_dispo`, `description`, `id_user`) VALUES
(2, 'journée entière', '2026-07-25', 'qui veut de l\'aide pour son jardinage ?? je suis de passage dans la ville!!', 2),
(3, 'matin', '2026-06-30', 'je peux aider pour faire des cours d\'anglais (je suis prof)', 9),
(4, 'journée entière', '2026-07-14', 'coach LOL pour devenir master', 10),
(5, 'matin', '2026-06-26', 'Qui pour se faire coach', 11),
(6, 'journée entière', '2026-07-31', 'je suis disponible toute la journée pour ce que vous voulez', 14);

-- --------------------------------------------------------

--
-- Structure de la table `interet`
--

CREATE TABLE `interet` (
  `id_user` int(11) NOT NULL,
  `id_dispo` int(11) NOT NULL,
  `statut` varchar(20) DEFAULT 'en_attente',
  `date_interet` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `interet`
--

INSERT INTO `interet` (`id_user`, `id_dispo`, `statut`, `date_interet`) VALUES
(10, 2, 'en_attente', '2026-06-24 19:44:37'),
(11, 2, 'en_attente', '2026-06-25 09:43:23'),
(12, 5, 'en_attente', '2026-06-25 09:59:26'),
(14, 5, 'en_attente', '2026-06-25 10:23:26');

-- --------------------------------------------------------

--
-- Structure de la table `proposition`
--

CREATE TABLE `proposition` (
  `id_prop` int(11) NOT NULL,
  `creneau` varchar(100) DEFAULT NULL,
  `date_prop` date DEFAULT NULL,
  `statut` varchar(20) DEFAULT 'en_attente',
  `id_user` int(11) NOT NULL,
  `id_annonce` int(11) NOT NULL,
  `id_activite` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `reagir`
--

CREATE TABLE `reagir` (
  `id_user` int(11) NOT NULL,
  `id_annonce` int(11) NOT NULL,
  `type` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `reagir`
--

INSERT INTO `reagir` (`id_user`, `id_annonce`, `type`) VALUES
(1, 8, 'coeur'),
(1, 8, 'rire'),
(1, 8, 'urgence'),
(8, 5, 'urgence'),
(8, 8, 'coeur'),
(8, 8, 'pouce'),
(8, 8, 'rire'),
(8, 8, 'urgence'),
(9, 8, 'urgence'),
(10, 8, 'urgence'),
(11, 8, 'urgence'),
(13, 8, 'urgence'),
(13, 10, 'coeur'),
(13, 10, 'rire'),
(14, 11, 'rire');

-- --------------------------------------------------------

--
-- Structure de la table `utilisateur`
--

CREATE TABLE `utilisateur` (
  `id_user` int(11) NOT NULL,
  `pseudo` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `mot_de_passe` varchar(255) NOT NULL,
  `role` varchar(20) DEFAULT 'user',
  `villageois_nom` varchar(100) DEFAULT NULL,
  `villageois_photo` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `utilisateur`
--

INSERT INTO `utilisateur` (`id_user`, `pseudo`, `email`, `mot_de_passe`, `role`, `villageois_nom`, `villageois_photo`) VALUES
(1, 'admin', 'admin@sos.fr', 'scrypt:32768:8:1$9WnKvQQv2SRlAaZp$bd611c858c318bef311aec849e5948ce4bc59b27e05709ee09f1fffca9688fe42f5b994adb3a898ce66963bc6a598b24bac7598e6c6e8d32faac35129d307f09', 'admin', 'Tom Nook', ''),
(2, 'souksana', 'test@sos.fr', 'scrypt:32768:8:1$hQlQLNgMKGAe54T7$ccda04c75976f1163f0e99aaebd19b4959dd9653c5405e60bad92da56b0a21dc6f2d77afd30c8f5b7273624d5c38ad3177a343c988ad393aa27961ebb18a641a', 'user', 'Isabelle', ''),
(3, 'zio', 'admin2@sos.fr', 'scrypt:32768:8:1$ZMxg5a8ypopAJwxW$08d4cd05c0ecdd494df241a6eb52e3c71ae7f4df39e840b1dc63a8035d5930dd85ac26d37e27737ed7d94a94922ced91495bf63f19e1c07ca1b3149814de4c66', 'admin', 'Follet', ''),
(4, 'maud', 'maud@sos.fr', 'scrypt:32768:8:1$P7GszntRhUqFvvlp$43196e73cc9d6a3811210dacabacf38d80507b4d6518b8a4de05dcaec0458cbe9491e2420fdac37db25f88c4d411f9afea75c163261a18af4cb22027f6e90288', 'user', 'Marshal', ''),
(5, 'prisca', 'prisca@sos.fr', 'scrypt:32768:8:1$yDEqit9k8WHReVIa$6e76d3c68e154ffc63bdf493ab995cbd2e0eb2305974d75f1b8cfc3e1cab21b2190cc616392c54fbba1adf20febfff6891389f6a68550fd91d65d17846a0d406', 'user', 'Raymond', ''),
(6, 'Gu', 'gugulugugu@gmail.com', 'scrypt:32768:8:1$pWjhKyRRcLoXcCx9$391968113dc97086a3c9f2fea34200a2c67cfdfc7f9fe20c55e2f471740593acb0438fb02c4bf8bcdb5278c0daa3b3ab4464f24dcf85ae6f926924b80a2870cc', 'user', 'Admiral', 'https://dodo.ac/np/images/0/0a/Admiral%27s_Photo_NH_Texture.png'),
(7, 'juju', 'blabla@gmail.com', 'scrypt:32768:8:1$AJfcxDb39qvRkyDy$444f18bc75f2564a28e9c108867879edc48ef85d6fedfdc190d96dd67270a1c2a6c056d7f9a214d8a54408e4c0e761019ee6068bae3b779dddfa615d7137f74b', 'user', 'Alfonso', 'https://dodo.ac/np/images/e/e8/Alfonso%27s_Photo_NH_Texture.png'),
(8, 'yugyeomiste', 'fofof@gmail.com', 'scrypt:32768:8:1$CqTpkOUPldP8DvYP$15db2bfe3674152b8d52ae6b8fd0843ab134d17290610c54be8c3e3a07fe5deacc9adbe3a89f979b244a0ad1ff6c5f7462c7a8895800bf072536feec88f54e9f', 'user', 'Bunnie', 'https://dodo.ac/np/images/f/f9/Bunnie%27s_Photo_NH_Texture.png'),
(9, 'Peppa pig', 'peppa@sos.fr', 'scrypt:32768:8:1$OhqeqjUzKZN7f0BZ$0b0f73eb79e7066cea6fbdb666d3886a894aaec56c409339d7017b93c9625026bf389849ecf64dcf9cd0cf8e06938757fdc3d0b8e7a87380730dedea02325c65', 'user', 'Curly', 'https://dodo.ac/np/images/7/73/Curly%27s_Photo_NH_Texture.png'),
(10, 'virgile', 'virgile@sos.fr', 'scrypt:32768:8:1$uTbfjE1PCb12nIb4$6d7bdfa4cb66d9ab7bcc5c7b50c167439292d04daf542b6dc70503ee049a2442011305f8483d9ca405c5338cb3b14ddea24383d34cea9f99447bb81392f00d76', 'user', 'Cranston', 'https://dodo.ac/np/images/3/39/Cranston%27s_Photo_NH_Texture.png'),
(11, 'Coach', 'coach@gmail.com', 'scrypt:32768:8:1$Wrq8wdMLIBbYuQne$dfbdebc74b169edac031e14f794ffc5093fe465ab788d8aba64a07880e193eb0a2f75a85c3a81ec9ab881fdde09abe8e6316d57ff4550fc98363b42f033c4817', 'user', 'Coach', 'https://dodo.ac/np/images/8/8d/Coach%27s_Photo_NH_Texture.png'),
(12, 'anookis', 'anookis@sos.fr', 'scrypt:32768:8:1$LNrvNytucW63BRFb$54cc745d5c6e79d22caba94113cdf46b04104035952df9d18228fb6f39b4e5ceba0d8480091874ff6946a67c9270471667a815b0d54e48c4ddc9a7dd003a31c1', 'user', 'Roscoe', 'https://dodo.ac/np/images/6/63/Roscoe%27s_Photo_NH_Texture.png'),
(13, 'eumma', 'eumma@gmail.com', 'scrypt:32768:8:1$eJcxg0B5rBkYTof6$2b6a9b9e6812a6b2cb453b48bce8db9a8fc1629ee4d8d75451858b86d7db957763644570776e3fa0609922930111e609af08702f5905efffe803690d0d308064', 'user', 'Mineru', 'https://dodo.ac/np/images/b/bb/Mineru%27s_Photo_NH_Texture.png'),
(14, 'parasi', 'parasi@gmail.com', 'scrypt:32768:8:1$T2XWkeR7KhmDrk3R$8e310a97d03415cfcc222b6fad68b252d62f769bc17be88abcb1aed63e1dcd0d29cd7a389dff06827794df69465f3875900b55b26ef842b85da8360c18558947', 'user', 'Dotty', 'https://dodo.ac/np/images/b/b1/Dotty%27s_Photo_NH_Texture.png'),
(15, 'random', 'random@gmail.com', 'scrypt:32768:8:1$k5AOOldl1CpPJnzM$f20111e53ab035ad8a293ea7ba9c2ecf33af8645e5815875d00aab41975d2e329e294c0f47110e25b0999a8576a00fc6e51f45726bb8a38692a86849d700eff8', 'user', 'Benjamin', 'https://dodo.ac/np/images/9/9e/Benjamin%27s_Photo_NH_Texture.png');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `activite`
--
ALTER TABLE `activite`
  ADD PRIMARY KEY (`id_activite`);

--
-- Index pour la table `annonce`
--
ALTER TABLE `annonce`
  ADD PRIMARY KEY (`id_annonce`),
  ADD KEY `id_user` (`id_user`);

--
-- Index pour la table `commentaire`
--
ALTER TABLE `commentaire`
  ADD PRIMARY KEY (`id_com`),
  ADD KEY `id_user` (`id_user`),
  ADD KEY `id_annonce` (`id_annonce`);

--
-- Index pour la table `disponibilite`
--
ALTER TABLE `disponibilite`
  ADD PRIMARY KEY (`id_dispo`),
  ADD KEY `id_user` (`id_user`);

--
-- Index pour la table `interet`
--
ALTER TABLE `interet`
  ADD PRIMARY KEY (`id_user`,`id_dispo`),
  ADD KEY `id_dispo` (`id_dispo`);

--
-- Index pour la table `proposition`
--
ALTER TABLE `proposition`
  ADD PRIMARY KEY (`id_prop`),
  ADD KEY `id_user` (`id_user`),
  ADD KEY `id_annonce` (`id_annonce`),
  ADD KEY `id_activite` (`id_activite`);

--
-- Index pour la table `reagir`
--
ALTER TABLE `reagir`
  ADD PRIMARY KEY (`id_user`,`id_annonce`,`type`),
  ADD KEY `id_annonce` (`id_annonce`);

--
-- Index pour la table `utilisateur`
--
ALTER TABLE `utilisateur`
  ADD PRIMARY KEY (`id_user`),
  ADD UNIQUE KEY `pseudo` (`pseudo`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `activite`
--
ALTER TABLE `activite`
  MODIFY `id_activite` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `annonce`
--
ALTER TABLE `annonce`
  MODIFY `id_annonce` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT pour la table `commentaire`
--
ALTER TABLE `commentaire`
  MODIFY `id_com` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT pour la table `disponibilite`
--
ALTER TABLE `disponibilite`
  MODIFY `id_dispo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT pour la table `proposition`
--
ALTER TABLE `proposition`
  MODIFY `id_prop` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `utilisateur`
--
ALTER TABLE `utilisateur`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `annonce`
--
ALTER TABLE `annonce`
  ADD CONSTRAINT `annonce_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `utilisateur` (`id_user`) ON DELETE CASCADE;

--
-- Contraintes pour la table `commentaire`
--
ALTER TABLE `commentaire`
  ADD CONSTRAINT `commentaire_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `utilisateur` (`id_user`) ON DELETE CASCADE,
  ADD CONSTRAINT `commentaire_ibfk_2` FOREIGN KEY (`id_annonce`) REFERENCES `annonce` (`id_annonce`) ON DELETE CASCADE;

--
-- Contraintes pour la table `disponibilite`
--
ALTER TABLE `disponibilite`
  ADD CONSTRAINT `disponibilite_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `utilisateur` (`id_user`) ON DELETE CASCADE;

--
-- Contraintes pour la table `interet`
--
ALTER TABLE `interet`
  ADD CONSTRAINT `interet_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `utilisateur` (`id_user`) ON DELETE CASCADE,
  ADD CONSTRAINT `interet_ibfk_2` FOREIGN KEY (`id_dispo`) REFERENCES `disponibilite` (`id_dispo`) ON DELETE CASCADE;

--
-- Contraintes pour la table `proposition`
--
ALTER TABLE `proposition`
  ADD CONSTRAINT `proposition_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `utilisateur` (`id_user`) ON DELETE CASCADE,
  ADD CONSTRAINT `proposition_ibfk_2` FOREIGN KEY (`id_annonce`) REFERENCES `annonce` (`id_annonce`) ON DELETE CASCADE,
  ADD CONSTRAINT `proposition_ibfk_3` FOREIGN KEY (`id_activite`) REFERENCES `activite` (`id_activite`) ON DELETE CASCADE;

--
-- Contraintes pour la table `reagir`
--
ALTER TABLE `reagir`
  ADD CONSTRAINT `reagir_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `utilisateur` (`id_user`) ON DELETE CASCADE,
  ADD CONSTRAINT `reagir_ibfk_2` FOREIGN KEY (`id_annonce`) REFERENCES `annonce` (`id_annonce`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
