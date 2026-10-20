# ★ sos villageois

projet de td | architecture logicielle  
e3 imac s2 | esiee paris | 2025/2026  

une plateforme d'entraide entre voisins, dans l'univers d'animal crossing. chaque habitant s'inscrit avec un villageois comme avatar, publie des annonces quand il a besoin d'un coup de main (jardinage, bricolage, courses…) et partage ses disponibilités pour aider les autres.

---

## plateforme de développement

développé et testé sous **windows 11** (xampp / mariadb 10.4) et **macOS**.  
backend : python 3 + flask 3.  
base de données : mysql / mariadb via `mysql-connector-python`.  
frontend : templates html + css + javascript vanilla (`fetch`), sans framework.  
api externe : [nookipedia](https://api.nookipedia.com/) pour la liste des villageois.

dépendances (`requirements.txt`) : flask, flask-cors, mysql-connector-python, werkzeug, requests, python-dotenv.

---

## lancer le projet

**1) base de données**  
créer une base `sos_villageois` puis importer `sos_villageois.sql` (phpmyadmin ou `mysql -u root sos_villageois < sos_villageois.sql`). le dump contient des utilisateurs, annonces, commentaires et réactions de démo.  
sans import, `init_db()` crée automatiquement les tables vides au lancement.

**2) environnement python**

```bash
python -m venv .venv
.venv\Scripts\activate        # windows
source .venv/bin/activate     # macOS
pip install -r requirements.txt
```

**3) fichier `.env`** (à la racine, ignoré par git)

```
SECRET_KEY=une-cle-secrete
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=sos_villageois
NOOKIPEDIA_KEY=            # optionnel
FLASK_DEBUG=true
```

toutes les variables ont une valeur par défaut, le `.env` n'est donc pas obligatoire pour une install xampp standard.

**4) lancement**

```bash
python app.py
```

le site tourne sur **http://localhost:5001** et la doc de l'api sur **http://localhost:5001/apidocs**.

---

## architecture

```
sos-villageois/
├── app.py              # routes flask : pages html + api rest json
├── modele.py           # accès bdd : création des tables, requêtes sql
├── sos_villageois.sql  # dump de la base avec données de démo
├── requirements.txt
├── static/
│   ├── css/style.css   # thème "nookphone"
│   ├── font/           # polices animal crossing
│   ├── img/            # logo, favicons, icônes, fonds d'écran
│   └── swagger.json    # spécification openapi de l'api
└── templates/
    ├── index.html      # écran d'accueil façon téléphone
    ├── connexion.html, inscription.html, profil.html, admin.html
    ├── swagger.html
    ├── annonce/        # liste, détail, nouvelle
    └── dispo/          # liste, détail, nouvelle
```

**séparation modèle / contrôleur / vue**  
`modele.py` est la seule couche qui parle à la base. `app.py` ne contient aucune requête sql : il valide les entrées, vérifie les droits et appelle les fonctions du modèle. les templates ne reçoivent aucune donnée de jinja, ils récupèrent tout en javascript via l'api.

**pages html vs api json**  
chaque page a deux types de routes :
- une route **page** (`GET /annonces`) qui renvoie juste le template html, protégée par `@login_required` (redirection vers `/connexion`)
- des routes **api** (`/api/annonces`) qui renvoient du json, protégées par `@api_login_required` (erreur `401`)

le navigateur charge la page vide, puis le javascript appelle l'api avec `fetch` et construit le dom.

---

## fonctionnalités

### ★ 1) comptes et rôles

- inscription avec choix d'un villageois comme avatar (liste récupérée depuis l'api nookipedia)
- connexion par email / mot de passe, session flask côté serveur
- mots de passe hachés avec `werkzeug.security` (scrypt), jamais stockés en clair
- deux rôles : `user` et `admin`
- modification du pseudo depuis le profil (refus si le pseudo est déjà pris)
- si un utilisateur est supprimé pendant qu'il est connecté, `verifier_session()` (exécuté avant chaque requête) vide sa session

### ★ 2) annonces

un habitant publie une demande d'aide avec un titre, une description et un type de tâche :
`jardinage, bricolage, courses, cuisine, informatique, garde d'animaux, déménagement, autre`.

- **tri** : plus récentes, plus anciennes, ou par urgence (nombre de réactions ‼️)
- **réactions** : ‼️ urgence, 💚 coeur, 😹 rire. un clic ajoute la réaction, un second clic l'enlève (toggle)
- **commentaires** sous chaque annonce
- **suppression** par l'auteur ou par un admin

### ★ 3) disponibilités

l'inverse des annonces : un habitant indique quand il est libre pour aider, avec une date et un créneau (`matin, après-midi, soir, journée entière`).

- seules les dispos à venir sont affichées (`date_dispo >= CURDATE()`), triées par date puis par créneau
- les autres habitants peuvent se déclarer **intéressés** (toggle). on ne peut pas être intéressé par sa propre dispo
- le détail d'une dispo affiche la liste des personnes intéressées

### ★ 4) administration

page `/admin` réservée aux admins : liste de tous les utilisateurs et suppression d'un compte. un admin ne peut pas se supprimer lui-même. grâce aux `ON DELETE CASCADE`, supprimer un utilisateur supprime aussi ses annonces, commentaires, réactions, dispos et intérêts.

---

## base de données

| table | rôle | clé primaire |
|-------|------|--------------|
| `Utilisateur` | comptes, rôle, villageois choisi | `id_user` |
| `Annonce` | demandes d'aide | `id_annonce` |
| `Commentaire` | commentaires sur une annonce | `id_com` |
| `Reagir` | réactions utilisateur → annonce | `(id_user, id_annonce, type)` |
| `Disponibilite` | créneaux où un habitant peut aider | `id_dispo` |
| `Interet` | utilisateur intéressé par une dispo | `(id_user, id_dispo)` |

les tables d'association `Reagir` et `Interet` utilisent une **clé primaire composée** : un utilisateur ne peut pas mettre deux fois la même réaction sur une annonce, ni être intéressé deux fois par la même dispo. c'est la base qui garantit la contrainte, pas seulement le code.

**comptage des réactions**  
la liste des annonces calcule les trois compteurs en une seule requête, avec une sous-requête `GROUP BY` par type de réaction jointe en `LEFT JOIN` :

```sql
LEFT JOIN (SELECT id_annonce, COUNT(*) AS cnt
           FROM Reagir WHERE type='urgence'
           GROUP BY id_annonce) r_u ON r_u.id_annonce = a.id_annonce
```

`COALESCE(r_u.cnt, 0)` remplace par 0 les annonces sans réaction. le tri "urgence" se fait ensuite directement en sql sur `urgence_count`.

---

## api rest

documentation interactive swagger sur `/apidocs` (spécification dans `static/swagger.json`).

| méthode | route | description | accès |
|---------|-------|-------------|-------|
| `POST` | `/api/connexion` | se connecter | public |
| `POST` | `/api/deconnexion` | se déconnecter | public |
| `POST` | `/api/users` | créer un compte | public |
| `GET` | `/api/users/me` | utilisateur connecté | connecté |
| `PUT` | `/api/profil` | modifier son pseudo | connecté |
| `GET` | `/api/villageois` | liste des villageois | public |
| `GET` | `/api/annonces?tri=recent\|ancien\|urgence` | liste des annonces | connecté |
| `POST` | `/api/annonces` | créer une annonce | connecté |
| `GET` | `/api/annonces/<id>` | détail + commentaires + réactions | connecté |
| `DELETE` | `/api/annonces/<id>` | supprimer une annonce | auteur / admin |
| `PUT` | `/api/annonces/<id>/reactions/<type>` | ajouter / retirer une réaction | connecté |
| `POST` | `/api/annonces/<id>/commentaires` | commenter | connecté |
| `GET` | `/api/dispos` | liste des dispos + mes intérêts | connecté |
| `POST` | `/api/dispos` | créer une dispo | connecté |
| `GET` | `/api/dispos/<id>` | détail + personnes intéressées | connecté |
| `DELETE` | `/api/dispos/<id>` | supprimer une dispo | auteur / admin |
| `PUT` | `/api/dispos/<id>/interet` | être intéressé / ne plus l'être | connecté (pas l'auteur) |
| `GET` | `/api/users` | liste des utilisateurs | admin |
| `DELETE` | `/api/users/<id>` | supprimer un utilisateur | admin |

**codes de retour** : `200` / `201` en cas de succès, `400` pour une saisie invalide, `401` si non connecté, `403` si pas les droits, `404` si la ressource n'existe pas, `409` pour un pseudo ou email déjà utilisé.

**choix des méthodes http**  
les actions toggle (réaction, intérêt) utilisent `PUT` plutôt que `POST` : le client indique l'état qu'il veut modifier sur une ressource identifiée par l'url, sans créer de nouvelle ressource avec un nouvel id.

**fallback pour les villageois**  
`/api/villageois` essaie d'abord nookipedia (si une clé est configurée), puis acnhapi, et en dernier recours renvoie une liste de 24 noms codée en dur. l'inscription marche donc même sans connexion internet.

---

## améliorations proposées par l'ia

une partie du td consistait à faire relire le code par une ia et à intégrer ses suggestions. elles sont signalées dans le code par un commentaire `# amélioration de l'IA`.

| amélioration | avant | après |
|--------------|-------|-------|
| identifiants bdd | dictionnaire `DB_CONFIG` écrit en dur dans `modele.py` | lus depuis `.env` avec `python-dotenv` |
| fermeture des connexions | `conn.close()` à la main à la fin de chaque fonction | context manager `get_db()` qui ferme curseur et connexion dans un `finally`, même en cas d'exception |
| index sql | aucun | index sur `Annonce(statut)`, `Annonce(date_creation)` et `Disponibilite(date_dispo)`, les colonnes utilisées dans les `WHERE` et `ORDER BY` |
| clé de session | écrite en dur | `SECRET_KEY` lue depuis l'environnement |
| mode debug | `debug=True` en dur | activé seulement si `FLASK_DEBUG=true` |

---

*flask 3 + mysql / mariadb + javascript vanilla | python 3*
