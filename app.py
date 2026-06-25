import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_cors import CORS
from datetime import date
from dotenv import load_dotenv
import modele
import requests as req

# amélioration de l'IA : charge les secrets depuis .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
CORS(app)

modele.init_db()
modele.seed_users()


# amélioration de l'IA : décorateur pour éviter la répétition de la vérification de session
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("id_user"):
            return redirect(url_for("connexion"))
        return f(*args, **kwargs)
    return decorated


@app.before_request
def verifier_session():
    id_user = session.get("id_user")
    if id_user and not modele.get_user_by_id(id_user):
        session.clear()


NOOKIPEDIA_KEY     = os.environ.get("NOOKIPEDIA_KEY", "")
NOOKIPEDIA_VERSION = "1.0.0"

REACTION_TYPES       = [('urgence', '‼️'), ('coeur', '💚'), ('rire', '😹')]
VALID_REACTION_TYPES = {t for t, _ in REACTION_TYPES}

VILLAGEOIS_MOCK = [
    "Marshal", "Raymond", "Ankha", "Diana", "Fauna", "Audie", "Judy",
    "Zucker", "Stitches", "Bob", "Goldie", "Dom", "Sherb", "Merengue",
    "Coco", "Marina", "Poppy", "Molly", "Lolly", "Lily", "Isabelle",
    "Celeste", "Flick", "C.J.",
]

# villageois : nookipedia > acnhapi > mock local
@app.route("/api/villageois")
def api_villageois():
    if NOOKIPEDIA_KEY:
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


TACHES   = ["jardinage", "bricolage", "courses", "cuisine", "informatique", "garde d'animaux", "déménagement", "autre"]
CRENEAUX = ["matin", "après-midi", "soir", "journée entière"]


# * accueil
@app.route("/")
def index():
    return render_template("index.html")


# * inscription
@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    erreur = None
    if request.method == "POST":
        # Longueurs max pour éviter qu'on insère n'importe quoi en base
        pseudo          = request.form.get("pseudo", "").strip()[:50]
        email           = request.form.get("email", "").strip()[:100]
        mdp             = request.form.get("mot_de_passe", "")
        confirm_mdp     = request.form.get("confirm_mdp", "")
        villageois_nom  = request.form.get("villageois_nom", "")
        villageois_photo = request.form.get("villageois_photo", "")
        if mdp != confirm_mdp:
            erreur = "les mots de passe ne correspondent pas"
        else:
            try:
                user = modele.add_user(pseudo, email, mdp, villageois_nom, villageois_photo)
                session["id_user"] = user["id_user"]
                session["pseudo"]  = user["pseudo"]
                session["role"]    = user["role"]
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
        mdp   = request.form.get("mot_de_passe")
        user  = modele.verifier_mdp(email, mdp)
        if user:
            session["id_user"] = user["id_user"]
            session["pseudo"]  = user["pseudo"]
            session["role"]    = user["role"]
            return redirect(url_for("index"))
        erreur = "email ou mot de passe incorrect"
    return render_template("connexion.html", erreur=erreur)


# * annonces
@app.route("/annonces")
@login_required
def annonces():
    tri = request.args.get("tri", "recent")
    if tri not in ('recent', 'ancien', 'urgence'):
        tri = 'recent'
    liste = modele.get_all_annonces(tri)
    return render_template("annonce/liste.html", annonces=liste, tri=tri)


@app.route("/annonces/nouvelle", methods=["GET", "POST"])
@login_required
def nouvelle_annonce():
    erreur = None
    if request.method == "POST":
        titre       = request.form.get("titre", "").strip()[:100]
        description = request.form.get("description", "").strip()[:2000]
        tache       = request.form.get("tache")
        # amélioration de l'IA : validation côté serveur du type de tâche
        if not titre or tache not in TACHES:
            erreur = "titre et type de tâche obligatoires"
        else:
            modele.add_annonce(titre, description, tache, session["id_user"])
            return redirect(url_for("annonces"))
    return render_template("annonce/nouvelle.html", taches=TACHES, erreur=erreur)


@app.route("/annonces/<int:id_annonce>")
@login_required
def annonce_detail(id_annonce):
    annonce = modele.get_annonce_by_id(id_annonce)
    if not annonce:
        return redirect(url_for("annonces"))
    commentaires  = modele.get_commentaires_annonce(id_annonce)
    reactions     = modele.get_reactions_annonce(id_annonce)
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
@login_required
def reagir_annonce(id_annonce):
    reaction_type = request.form.get("type")
    if reaction_type in VALID_REACTION_TYPES:
        modele.toggle_reaction(session["id_user"], id_annonce, reaction_type)
    return redirect(url_for("annonce_detail", id_annonce=id_annonce))


@app.route("/annonces/<int:id_annonce>/commenter", methods=["POST"])
@login_required
def commenter_annonce(id_annonce):
    # amélioration de l'IA : limite la longueur des commentaires
    contenu = request.form.get("contenu", "").strip()[:1000]
    if contenu:
        modele.add_commentaire(contenu, session["id_user"], id_annonce)
    return redirect(url_for("annonce_detail", id_annonce=id_annonce))


@app.route("/annonces/<int:id_annonce>/supprimer", methods=["POST"])
@login_required
def supprimer_annonce(id_annonce):
    annonce = modele.get_annonce_by_id(id_annonce)
    if annonce and (annonce["id_user"] == session["id_user"] or session.get("role") == "admin"):
        modele.delete_annonce(id_annonce)
    return redirect(url_for("annonces"))


# * disponibilités
@app.route("/dispos")
@login_required
def dispos():
    liste       = modele.get_all_dispos()
    mes_interets = modele.get_user_interets(session["id_user"])
    return render_template("dispo/liste.html", dispos=liste, mes_interets=mes_interets)


@app.route("/dispos/<int:id_dispo>")
@login_required
def dispo_detail(id_dispo):
    dispo = modele.get_dispo_by_id(id_dispo)
    if not dispo:
        return redirect(url_for("dispos"))
    interets      = modele.get_interets_dispo(id_dispo)
    user_interesse = session["id_user"] in {i["id_user"] for i in interets}
    return render_template("dispo/detail.html", dispo=dispo, interets=interets, user_interesse=user_interesse)


@app.route("/dispos/<int:id_dispo>/interesse", methods=["POST"])
@login_required
def interesse_dispo(id_dispo):
    dispo = modele.get_dispo_by_id(id_dispo)
    if dispo and dispo["id_user"] != session["id_user"]:
        modele.toggle_interet(session["id_user"], id_dispo)
    return redirect(request.referrer or url_for("dispos"))


@app.route("/dispos/nouvelle", methods=["GET", "POST"])
@login_required
def nouvelle_dispo():
    erreur = None
    if request.method == "POST":
        date_dispo  = request.form.get("date_dispo")
        creneau     = request.form.get("creneau")
        description = request.form.get("description", "").strip()[:500]
        # amélioration de l'IA : validation côté serveur du créneau
        if not date_dispo or creneau not in CRENEAUX:
            erreur = "date et créneau obligatoires"
        else:
            modele.add_dispo(date_dispo, creneau, description, session["id_user"])
            return redirect(url_for("dispos"))
    return render_template("dispo/nouvelle.html", creneaux=CRENEAUX, erreur=erreur, today=date.today().isoformat())


@app.route("/dispos/<int:id_dispo>/supprimer", methods=["POST"])
@login_required
def supprimer_dispo(id_dispo):
    dispo = modele.get_dispo_by_id(id_dispo)
    if dispo and (dispo["id_user"] == session["id_user"] or session.get("role") == "admin"):
        modele.delete_dispo(id_dispo)
    return redirect(url_for("dispos"))


# * profil
@app.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    erreur = None
    succes = None
    if request.method == "POST":
        nouveau_pseudo = request.form.get("pseudo", "").strip()[:50]
        if not nouveau_pseudo:
            erreur = "le pseudo ne peut pas être vide"
        elif nouveau_pseudo == session["pseudo"]:
            pass
        else:
            try:
                modele.update_pseudo(session["id_user"], nouveau_pseudo)
                session["pseudo"] = nouveau_pseudo
                succes = "pseudo mis à jour !"
            except Exception:
                erreur = "ce pseudo est déjà pris"
    user = modele.get_user_by_id(session["id_user"])
    return render_template("profil.html", user=user, erreur=erreur, succes=succes)


# * déconnexion
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
    if id_user != session.get("id_user"): # * on peut pas se supprimer soi-meme :p
        modele.delete_user(id_user)
    return redirect(url_for("admin"))


if __name__ == "__main__":
    # amélioration de l'IA : debug contrôlé par .env, pas hardcodé
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, port=5001)
