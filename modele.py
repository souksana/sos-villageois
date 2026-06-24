import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

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

# * utilisateurs

def add_user(pseudo, email, mot_de_passe, villageois_nom, villageois_photo):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = generate_password_hash(mot_de_passe)
    cursor.execute(
        "INSERT INTO Utilisateur (pseudo, email, mot_de_passe, villageois_nom, villageois_photo) VALUES (%s, %s, %s, %s, %s)",
        (pseudo, email, hashed, villageois_nom, villageois_photo)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return get_user_by_id(new_id)

def get_user_by_id(id_user):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Utilisateur WHERE id_user = %s", (id_user,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Utilisateur WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def verifier_mdp(email, mot_de_passe):
    user = get_user_by_email(email)
    if user and check_password_hash(user["mot_de_passe"], mot_de_passe):
        return user
    return None
    
# * annonces

def get_all_annonces():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, u.pseudo, u.villageois_photo
        FROM Annonce a
        JOIN Utilisateur u ON a.id_user = u.id_user
        WHERE a.statut = 'ouverte'
        ORDER BY a.date_creation DESC
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_annonce_by_id(id_annonce):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, u.pseudo, u.villageois_photo
        FROM Annonce a
        JOIN Utilisateur u ON a.id_user = u.id_user
        WHERE a.id_annonce = %s
    """, (id_annonce,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def add_annonce(titre, description, tache, id_user):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Annonce (titre, description, tache, id_user) VALUES (%s, %s, %s, %s)",
        (titre, description, tache, id_user)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return get_annonce_by_id(new_id)

def delete_annonce(id_annonce):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Annonce WHERE id_annonce = %s", (id_annonce,))
    conn.commit()
    cursor.close()
    conn.close()

def get_commentaires_annonce(id_annonce):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.*, u.pseudo, u.villageois_photo
        FROM Commentaire c
        JOIN Utilisateur u ON c.id_user = u.id_user
        WHERE c.id_annonce = %s
        ORDER BY c.date_com ASC
    """, (id_annonce,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def add_commentaire(contenu, id_user, id_annonce):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Commentaire (contenu, id_user, id_annonce) VALUES (%s, %s, %s)",
        (contenu, id_user, id_annonce)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_user, pseudo, email, role, villageois_nom FROM Utilisateur ORDER BY id_user")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def delete_user(id_user):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Utilisateur WHERE id_user = %s", (id_user,))
    conn.commit()
    cursor.close()
    conn.close()

# * comptes de test
def seed_users():
    comptes = [
        ("admin",    "admin@sos.fr",   "admin123",  "Tom Nook",  "", "admin"),
        ("zio", "admin2@sos.fr",    "admin123",   "Follet",  "", "admin"),
        ("souksana", "test@sos.fr",    "test123",   "Isabelle",  "", "user"),
    ]
    for pseudo, email, mdp, vnom, vphoto, role in comptes:
        if not get_user_by_email(email):
            conn = get_connection()
            cursor = conn.cursor()
            hashed = generate_password_hash(mdp)
            cursor.execute(
                "INSERT INTO Utilisateur (pseudo, email, mot_de_passe, villageois_nom, villageois_photo, role) VALUES (%s, %s, %s, %s, %s, %s)",
                (pseudo, email, hashed, vnom, vphoto, role)
            )
            conn.commit()
            cursor.close()
            conn.close()
