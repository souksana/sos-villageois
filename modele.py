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
            PRIMARY KEY (id_user, id_annonce, type),
            FOREIGN KEY (id_user) REFERENCES Utilisateur(id_user) ON DELETE CASCADE,
            FOREIGN KEY (id_annonce) REFERENCES Annonce(id_annonce) ON DELETE CASCADE
        )
    """)
    try:
        cursor.execute("ALTER TABLE Reagir DROP PRIMARY KEY, ADD PRIMARY KEY (id_user, id_annonce, type)")
        conn.commit()
    except:
        pass

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

def get_all_annonces(tri='recent'):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    order = {
        'ancien': 'a.date_creation ASC',
        'urgence': 'urgence_count DESC, a.date_creation DESC',
    }.get(tri, 'a.date_creation DESC')
    cursor.execute(f"""
        SELECT a.*, u.pseudo, u.villageois_photo,
          COALESCE(r_u.cnt, 0) AS urgence_count,
          COALESCE(r_c.cnt, 0) AS coeur_count,
          COALESCE(r_r.cnt, 0) AS rire_count
        FROM Annonce a
        JOIN Utilisateur u ON a.id_user = u.id_user
        LEFT JOIN (SELECT id_annonce, COUNT(*) AS cnt FROM Reagir WHERE type='urgence' GROUP BY id_annonce) r_u ON r_u.id_annonce = a.id_annonce
        LEFT JOIN (SELECT id_annonce, COUNT(*) AS cnt FROM Reagir WHERE type='coeur' GROUP BY id_annonce) r_c ON r_c.id_annonce = a.id_annonce
        LEFT JOIN (SELECT id_annonce, COUNT(*) AS cnt FROM Reagir WHERE type='rire' GROUP BY id_annonce) r_r ON r_r.id_annonce = a.id_annonce
        WHERE a.statut = 'ouverte'
        ORDER BY {order}
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

def get_reactions_annonce(id_annonce):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT type, COUNT(*) AS count FROM Reagir WHERE id_annonce = %s GROUP BY type",
        (id_annonce,)
    )
    result = {row['type']: row['count'] for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    return result

def get_user_reactions(id_user, id_annonce):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT type FROM Reagir WHERE id_user = %s AND id_annonce = %s",
        (id_user, id_annonce)
    )
    result = {row[0] for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    return result

def toggle_reaction(id_user, id_annonce, reaction_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM Reagir WHERE id_user=%s AND id_annonce=%s AND type=%s",
        (id_user, id_annonce, reaction_type)
    )
    if cursor.fetchone():
        cursor.execute(
            "DELETE FROM Reagir WHERE id_user=%s AND id_annonce=%s AND type=%s",
            (id_user, id_annonce, reaction_type)
        )
    else:
        cursor.execute(
            "INSERT INTO Reagir (id_user, id_annonce, type) VALUES (%s, %s, %s)",
            (id_user, id_annonce, reaction_type)
        )
    conn.commit()
    cursor.close()
    conn.close()

def get_all_dispos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT d.*, u.pseudo, u.villageois_photo,
            COUNT(i.id_user) AS interet_count
        FROM Disponibilite d
        JOIN Utilisateur u ON d.id_user = u.id_user
        LEFT JOIN Interet i ON i.id_dispo = d.id_dispo
        WHERE d.date_dispo >= CURDATE()
        GROUP BY d.id_dispo
        ORDER BY d.date_dispo ASC,
            FIELD(d.creneau, 'matin', 'après-midi', 'soir', 'journée entière')
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_dispo_by_id(id_dispo):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT d.*, u.pseudo, u.villageois_photo
        FROM Disponibilite d
        JOIN Utilisateur u ON d.id_user = u.id_user
        WHERE d.id_dispo = %s
    """, (id_dispo,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def add_dispo(date_dispo, creneau, description, id_user):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Disponibilite (date_dispo, creneau, description, id_user) VALUES (%s, %s, %s, %s)",
        (date_dispo, creneau, description, id_user)
    )
    conn.commit()
    cursor.close()
    conn.close()

def delete_dispo(id_dispo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Disponibilite WHERE id_dispo = %s", (id_dispo,))
    conn.commit()
    cursor.close()
    conn.close()

def update_pseudo(id_user, nouveau_pseudo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Utilisateur SET pseudo=%s WHERE id_user=%s", (nouveau_pseudo, id_user))
    conn.commit()
    cursor.close()
    conn.close()

def toggle_interet(id_user, id_dispo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM Interet WHERE id_user=%s AND id_dispo=%s", (id_user, id_dispo))
    if cursor.fetchone():
        cursor.execute("DELETE FROM Interet WHERE id_user=%s AND id_dispo=%s", (id_user, id_dispo))
    else:
        cursor.execute("INSERT INTO Interet (id_user, id_dispo) VALUES (%s, %s)", (id_user, id_dispo))
    conn.commit()
    cursor.close()
    conn.close()

def get_interets_dispo(id_dispo):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT i.*, u.pseudo, u.villageois_photo
        FROM Interet i
        JOIN Utilisateur u ON i.id_user = u.id_user
        WHERE i.id_dispo = %s
        ORDER BY i.date_interet ASC
    """, (id_dispo,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_user_interets(id_user):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_dispo FROM Interet WHERE id_user=%s", (id_user,))
    result = {row[0] for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    return result

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
