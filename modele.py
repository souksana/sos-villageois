import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "sos_villageois"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Utilisateur (
            id_user INT AUTO_INCREMENT PRIMARY KEY,
            pseudo VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            mot_de_passe VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'user',
            villageois_nom VARCHAR(100),
            villageois_photo VARCHAR(255)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Annonce (
            id_annonce INT AUTO_INCREMENT PRIMARY KEY,
            titre VARCHAR(100) NOT NULL,
            description TEXT,
            tache VARCHAR(100),
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
            statut VARCHAR(20) DEFAULT 'ouverte',
            id_user INT NOT NULL,
            FOREIGN KEY (id_user) REFERENCES Utilisateur(id_user) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Commentaire (
            id_com INT AUTO_INCREMENT PRIMARY KEY,
            contenu TEXT NOT NULL,
            date_com DATETIME DEFAULT CURRENT_TIMESTAMP,
            id_user INT NOT NULL,
            id_annonce INT NOT NULL,
            FOREIGN KEY (id_user) REFERENCES Utilisateur(id_user) ON DELETE CASCADE,
            FOREIGN KEY (id_annonce) REFERENCES Annonce(id_annonce) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Activite (
            id_activite INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(100) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Disponibilite (
            id_dispo INT AUTO_INCREMENT PRIMARY KEY,
            creneau VARCHAR(100),
            date_dispo DATE,
            description TEXT,
            id_user INT NOT NULL,
            FOREIGN KEY (id_user) REFERENCES Utilisateur(id_user) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Reagir (
            id_user INT NOT NULL,
            id_annonce INT NOT NULL,
            type VARCHAR(20) NOT NULL,
            PRIMARY KEY (id_user, id_annonce),
            FOREIGN KEY (id_user) REFERENCES Utilisateur(id_user) ON DELETE CASCADE,
            FOREIGN KEY (id_annonce) REFERENCES Annonce(id_annonce) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Interet (
            id_user INT NOT NULL,
            id_dispo INT NOT NULL,
            statut VARCHAR(20) DEFAULT 'en_attente',
            date_interet DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id_user, id_dispo),
            FOREIGN KEY (id_user) REFERENCES Utilisateur(id_user) ON DELETE CASCADE,
            FOREIGN KEY (id_dispo) REFERENCES Disponibilite(id_dispo) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Proposition (
            id_prop INT AUTO_INCREMENT PRIMARY KEY,
            creneau VARCHAR(100),
            date_prop DATE,
            statut VARCHAR(20) DEFAULT 'en_attente',
            id_user INT NOT NULL,
            id_annonce INT NOT NULL,
            id_activite INT NOT NULL,
            FOREIGN KEY (id_user) REFERENCES Utilisateur(id_user) ON DELETE CASCADE,
            FOREIGN KEY (id_annonce) REFERENCES Annonce(id_annonce) ON DELETE CASCADE,
            FOREIGN KEY (id_activite) REFERENCES Activite(id_activite) ON DELETE CASCADE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
