import os
from contextlib import contextmanager
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash


# amélioration de l'IA : credentials chargés depuis .env
def get_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "sos_villageois")
    )


# amélioration de l'IA : context manager pour fermer la connexion même en cas d'erreur
@contextmanager
def get_db(dictionary=True):
    conn = get_connection()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield conn, cursor
    finally:
        cursor.close()
        conn.close()


def init_db():
    with get_db(dictionary=False) as (conn, cursor):

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

        conn.commit()

    # amélioration de l'IA : index sur les colonnes filtrées pour accélérer les requêtes
    with get_db(dictionary=False) as (conn, cursor):
        for sql in [
            "CREATE INDEX idx_annonce_statut ON Annonce(statut)",
            "CREATE INDEX idx_annonce_date   ON Annonce(date_creation)",
            "CREATE INDEX idx_dispo_date     ON Disponibilite(date_dispo)",
        ]:
            try:
                cursor.execute(sql)
                conn.commit()
            except mysql.connector.errors.DatabaseError:
                pass  # index déjà présent


# * utilisateurs

def add_user(pseudo, email, mot_de_passe, villageois_nom, villageois_photo):
    with get_db(dictionary=False) as (conn, cursor):
        hashed = generate_password_hash(mot_de_passe)
        cursor.execute(
            "INSERT INTO Utilisateur (pseudo, email, mot_de_passe, villageois_nom, villageois_photo) VALUES (%s, %s, %s, %s, %s)",
            (pseudo, email, hashed, villageois_nom, villageois_photo)
        )
        conn.commit()
        new_id = cursor.lastrowid
    return get_user_by_id(new_id)

def get_user_by_id(id_user):
    with get_db() as (_, cursor):
        cursor.execute("SELECT * FROM Utilisateur WHERE id_user = %s", (id_user,))
        return cursor.fetchone()

def get_user_by_email(email):
    with get_db() as (_, cursor):
        cursor.execute("SELECT * FROM Utilisateur WHERE email = %s", (email,))
        return cursor.fetchone()

def verifier_mdp(email, mot_de_passe):
    user = get_user_by_email(email)
    if user and check_password_hash(user["mot_de_passe"], mot_de_passe):
        return user
    return None


# * annonces

def get_all_annonces(tri='recent'):
    order = {
        'ancien':  'a.date_creation ASC',
        'urgence': 'urgence_count DESC, a.date_creation DESC',
    }.get(tri, 'a.date_creation DESC')
    with get_db() as (_, cursor):
        cursor.execute(f"""
            SELECT a.*, u.pseudo, u.villageois_photo,
              COALESCE(r_u.cnt, 0) AS urgence_count,
              COALESCE(r_c.cnt, 0) AS coeur_count,
              COALESCE(r_r.cnt, 0) AS rire_count
            FROM Annonce a
            JOIN Utilisateur u ON a.id_user = u.id_user
            LEFT JOIN (SELECT id_annonce, COUNT(*) AS cnt FROM Reagir WHERE type='urgence' GROUP BY id_annonce) r_u ON r_u.id_annonce = a.id_annonce
            LEFT JOIN (SELECT id_annonce, COUNT(*) AS cnt FROM Reagir WHERE type='coeur'   GROUP BY id_annonce) r_c ON r_c.id_annonce = a.id_annonce
            LEFT JOIN (SELECT id_annonce, COUNT(*) AS cnt FROM Reagir WHERE type='rire'    GROUP BY id_annonce) r_r ON r_r.id_annonce = a.id_annonce
            WHERE a.statut = 'ouverte'
            ORDER BY {order}
        """)
        return cursor.fetchall()

def get_annonce_by_id(id_annonce):
    with get_db() as (_, cursor):
        cursor.execute("""
            SELECT a.*, u.pseudo, u.villageois_photo
            FROM Annonce a
            JOIN Utilisateur u ON a.id_user = u.id_user
            WHERE a.id_annonce = %s
        """, (id_annonce,))
        return cursor.fetchone()

def add_annonce(titre, description, tache, id_user):
    with get_db(dictionary=False) as (conn, cursor):
        cursor.execute(
            "INSERT INTO Annonce (titre, description, tache, id_user) VALUES (%s, %s, %s, %s)",
            (titre, description, tache, id_user)
        )
        conn.commit()
        new_id = cursor.lastrowid
    return get_annonce_by_id(new_id)

def delete_annonce(id_annonce):
    with get_db(dictionary=False) as (conn, cursor):
        cursor.execute("DELETE FROM Annonce WHERE id_annonce = %s", (id_annonce,))
        conn.commit()

def get_commentaires_annonce(id_annonce):
    with get_db() as (_, cursor):
        cursor.execute("""
            SELECT c.*, u.pseudo, u.villageois_photo
            FROM Commentaire c
            JOIN Utilisateur u ON c.id_user = u.id_user
            WHERE c.id_annonce = %s
            ORDER BY c.date_com ASC
        """, (id_annonce,))
        return cursor.fetchall()

def add_commentaire(contenu, id_user, id_annonce):
    with get_db(dictionary=False) as (conn, cursor):
        cursor.execute(
            "INSERT INTO Commentaire (contenu, id_user, id_annonce) VALUES (%s, %s, %s)",
            (contenu, id_user, id_annonce)
        )
        conn.commit()

def get_reactions_annonce(id_annonce):
    with get_db() as (_, cursor):
        cursor.execute(
            "SELECT type, COUNT(*) AS count FROM Reagir WHERE id_annonce = %s GROUP BY type",
            (id_annonce,)
        )
        return {row['type']: row['count'] for row in cursor.fetchall()}

def get_user_reactions(id_user, id_annonce):
    with get_db(dictionary=False) as (_, cursor):
        cursor.execute(
            "SELECT type FROM Reagir WHERE id_user = %s AND id_annonce = %s",
            (id_user, id_annonce)
        )
        return {row[0] for row in cursor.fetchall()}

def toggle_reaction(id_user, id_annonce, reaction_type):
    with get_db(dictionary=False) as (conn, cursor):
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


# * disponibilités

def get_all_dispos():
    with get_db() as (_, cursor):
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
        return cursor.fetchall()

def get_dispo_by_id(id_dispo):
    with get_db() as (_, cursor):
        cursor.execute("""
            SELECT d.*, u.pseudo, u.villageois_photo
            FROM Disponibilite d
            JOIN Utilisateur u ON d.id_user = u.id_user
            WHERE d.id_dispo = %s
        """, (id_dispo,))
        return cursor.fetchone()

def add_dispo(date_dispo, creneau, description, id_user):
    with get_db(dictionary=False) as (conn, cursor):
        cursor.execute(
            "INSERT INTO Disponibilite (date_dispo, creneau, description, id_user) VALUES (%s, %s, %s, %s)",
            (date_dispo, creneau, description, id_user)
        )
        conn.commit()

def delete_dispo(id_dispo):
    with get_db(dictionary=False) as (conn, cursor):
        cursor.execute("DELETE FROM Disponibilite WHERE id_dispo = %s", (id_dispo,))
        conn.commit()

def toggle_interet(id_user, id_dispo):
    with get_db(dictionary=False) as (conn, cursor):
        cursor.execute("SELECT 1 FROM Interet WHERE id_user=%s AND id_dispo=%s", (id_user, id_dispo))
        if cursor.fetchone():
            cursor.execute("DELETE FROM Interet WHERE id_user=%s AND id_dispo=%s", (id_user, id_dispo))
        else:
            cursor.execute("INSERT INTO Interet (id_user, id_dispo) VALUES (%s, %s)", (id_user, id_dispo))
        conn.commit()

def get_interets_dispo(id_dispo):
    with get_db() as (_, cursor):
        cursor.execute("""
            SELECT i.*, u.pseudo, u.villageois_photo
            FROM Interet i
            JOIN Utilisateur u ON i.id_user = u.id_user
            WHERE i.id_dispo = %s
            ORDER BY i.date_interet ASC
        """, (id_dispo,))
        return cursor.fetchall()

def get_user_interets(id_user):
    with get_db(dictionary=False) as (_, cursor):
        cursor.execute("SELECT id_dispo FROM Interet WHERE id_user=%s", (id_user,))
        return {row[0] for row in cursor.fetchall()}


# * profil

def update_pseudo(id_user, nouveau_pseudo):
    with get_db(dictionary=False) as (conn, cursor):
        cursor.execute("UPDATE Utilisateur SET pseudo=%s WHERE id_user=%s", (nouveau_pseudo, id_user))
        conn.commit()


# * admin

def get_all_users():
    with get_db() as (_, cursor):
        cursor.execute("SELECT id_user, pseudo, email, role, villageois_nom FROM Utilisateur ORDER BY id_user")
        return cursor.fetchall()

def delete_user(id_user):
    with get_db(dictionary=False) as (conn, cursor):
        cursor.execute("DELETE FROM Utilisateur WHERE id_user = %s", (id_user,))
        conn.commit()


# * comptes de test

def seed_users():
    comptes = [
        ("admin",    "admin@sos.fr",  "admin123", "Tom Nook",  "", "admin"),
        ("zio",      "admin2@sos.fr", "admin123", "Follet",    "", "admin"),
        ("souksana", "test@sos.fr",   "test123",  "Isabelle",  "", "user"),
    ]
    for pseudo, email, mdp, vnom, vphoto, role in comptes:
        if not get_user_by_email(email):
            with get_db(dictionary=False) as (conn, cursor):
                hashed = generate_password_hash(mdp)
                cursor.execute(
                    "INSERT INTO Utilisateur (pseudo, email, mot_de_passe, villageois_nom, villageois_photo, role) VALUES (%s, %s, %s, %s, %s, %s)",
                    (pseudo, email, hashed, vnom, vphoto, role)
                )
                conn.commit()
