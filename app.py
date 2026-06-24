from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_cors import CORS
import modele
import requests as req

app = Flask(__name__)
app.secret_key = "sos-villageois-secret"
CORS(app)

modele.init_db()
modele.seed_users()

NOOKIPEDIA_KEY = "dfe94752-dd22-4e96-85a0-eb7eb0804afa"
NOOKIPEDIA_VERSION = "1.0.0"

REACTION_TYPES = [('urgence', '‼️'), ('coeur', '💚'), ('rire', '😹')]
VALID_REACTION_TYPES = {t for t, _ in REACTION_TYPES}

# * liste de secours si aucune api dispo
VILLAGEOIS_MOCK = [
    "Marshal", "Raymond", "Ankha", "Diana", "Fauna", "Audie", "Judy",
    "Zucker", "Stitches", "Bob", "Goldie", "Dom", "Sherb", "Merengue",
    "Coco", "Marina", "Poppy", "Molly", "Lolly", "Lily", "Isabelle",
    "Celeste", "Flick", "C.J.",
]

# * villageois : nookipedia > acnhapi > mock local
@app.route("/api/villageois")
def api_villageois():
    if NOOKIPEDIA_KEY != "nookipedia-api-key":  # * si la clé est renseignée, on tente l'api nookipedia
        try:
            response = req.get(
                "https://api.nookipedia.com/villagers",
                headers={"X-API-Key": NOOKIPEDIA_KEY, "Accept-Version": NOOKIPEDIA_VERSION},
                params={"nhdetails": "true", "limit": "50"},
                timeout=5
            )
            data = response.json()
            return jsonify([
                {
                    "name": v["name"],
                    "image_url": (v.get("nh_details") or {}).get("photo_url") or v.get("image_url", ""),
                    "species": v.get("species", "")
                }
                for v in data
            ])
        except Exception:
            pass

    try:
        response = req.get("https://acnhapi.com/v1a/villagers", timeout=5)
        data = response.json()
        return jsonify([
            {"name": v["name"]["name-USen"], "image_url": v["image_uri"], "species": v.get("species", "")}
            for v in data[:50]
        ])
    except Exception:
        return jsonify([{"name": n, "image_url": "", "species": ""} for n in VILLAGEOIS_MOCK])

TACHES = ["jardinage", "bricolage", "courses", "cuisine", "informatique", "garde d'animaux", "déménagement", "autre"]
# * accueil
@app.route("/")
def index():
    return render_template("index.html")

# * inscription
@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    erreur = None
    if request.method == "POST":
        pseudo = request.form.get("pseudo")
        email = request.form.get("email")
        mdp = request.form.get("mot_de_passe")
        villageois_nom = request.form.get("villageois_nom")
        villageois_photo = request.form.get("villageois_photo")
        confirm_mdp = request.form.get("confirm_mdp")
        if mdp != confirm_mdp:
            erreur = "les mots de passe ne correspondent pas"
        else:
            try:
                user = modele.add_user(pseudo, email, mdp, villageois_nom, villageois_photo)
                session["id_user"] = user["id_user"]
                session["pseudo"] = user["pseudo"]
                session["role"] = user["role"]
                return redirect(url_for("index"))
            except Exception:
                erreur = "pseudo ou email déjà utilisé"
    return render_template("inscription.html", erreur=erreur)

# * connexion
@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    erreur = None
    if request.method == "POST":
        email = request.form.get("email")
        mdp = request.form.get("mot_de_passe")
        user = modele.verifier_mdp(email, mdp)
        if user:
            session["id_user"] = user["id_user"]
            session["pseudo"] = user["pseudo"]
            session["role"] = user["role"]
            return redirect(url_for("index"))
        erreur = "email ou mot de passe incorrect"
    return render_template("connexion.html", erreur=erreur)

# * annonces
@app.route("/annonces")
def annonces():
    if not session.get("id_user"):
        return redirect(url_for("connexion"))
    tri = request.args.get("tri", "recent")
    if tri not in ('recent', 'ancien', 'urgence'):
        tri = 'recent'
    liste = modele.get_all_annonces(tri)
    return render_template("annonce/liste.html", annonces=liste, tri=tri)

@app.route("/annonces/nouvelle", methods=["GET", "POST"])
def nouvelle_annonce():
    if not session.get("id_user"):
        return redirect(url_for("connexion"))
    erreur = None
    if request.method == "POST":
        titre = request.form.get("titre", "").strip()
        description = request.form.get("description", "").strip()
        tache = request.form.get("tache")
        if not titre or not tache:
            erreur = "titre et type de tâche obligatoires"
        else:
            modele.add_annonce(titre, description, tache, session["id_user"])
            return redirect(url_for("annonces"))
    return render_template("annonce/nouvelle.html", taches=TACHES, erreur=erreur)

@app.route("/annonces/<int:id_annonce>")
def annonce_detail(id_annonce):
    if not session.get("id_user"):
        return redirect(url_for("connexion"))
    annonce = modele.get_annonce_by_id(id_annonce)
    if not annonce:
        return redirect(url_for("annonces"))
    commentaires = modele.get_commentaires_annonce(id_annonce)
    reactions = modele.get_reactions_annonce(id_annonce)
    user_reactions = modele.get_user_reactions(session["id_user"], id_annonce)
    return render_template(
        "annonce/detail.html",
        annonce=annonce,
        commentaires=commentaires,
        reactions=reactions,
        user_reactions=user_reactions,
        reaction_types=REACTION_TYPES
    )

@app.route("/annonces/<int:id_annonce>/reagir", methods=["POST"])
def reagir_annonce(id_annonce):
    if not session.get("id_user"):
        return redirect(url_for("connexion"))
    reaction_type = request.form.get("type")
    if reaction_type in VALID_REACTION_TYPES:
        modele.toggle_reaction(session["id_user"], id_annonce, reaction_type)
    return redirect(url_for("annonce_detail", id_annonce=id_annonce))

@app.route("/annonces/<int:id_annonce>/commenter", methods=["POST"])
def commenter_annonce(id_annonce):
    if not session.get("id_user"):
        return redirect(url_for("connexion"))
    contenu = request.form.get("contenu", "").strip()
    if contenu:
        modele.add_commentaire(contenu, session["id_user"], id_annonce)
    return redirect(url_for("annonce_detail", id_annonce=id_annonce))

@app.route("/annonces/<int:id_annonce>/supprimer", methods=["POST"])
def supprimer_annonce(id_annonce):
    if not session.get("id_user"):
        return redirect(url_for("connexion"))
    annonce = modele.get_annonce_by_id(id_annonce)
    if annonce and (annonce["id_user"] == session["id_user"] or session.get("role") == "admin"):
        modele.delete_annonce(id_annonce)
    return redirect(url_for("annonces"))

# * profil
@app.route("/profil")
def profil():
    if not session.get("id_user"):
        return redirect(url_for("connexion"))
    user = modele.get_user_by_id(session["id_user"])
    return render_template("profil.html", user=user)

# * deconnexion
@app.route("/deconnexion")
def deconnexion():
    session.clear()
    return redirect(url_for("connexion"))

# * admin
@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    users = modele.get_all_users()
    return render_template("admin.html", users=users)

@app.route("/admin/supprimer/<int:id_user>", methods=["POST"])
def admin_supprimer_user(id_user):
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    if id_user != session.get("id_user"):  # * on peut pas se supprimer soi-meme
        modele.delete_user(id_user)
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True, port=5001)  
