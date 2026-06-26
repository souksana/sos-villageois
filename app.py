import os
from functools import wraps
from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
import modele
import requests as req

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
CORS(app)

modele.init_db()
modele.seed_users()


def to_dict(row):
    if row is None:
        return None
    return {
        k: v.isoformat() if isinstance(v, (date, datetime)) else v
        for k, v in row.items()
    }


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("id_user"):
            return redirect(url_for("connexion"))
        return f(*args, **kwargs)
    return decorated


def api_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("id_user"):
            return jsonify({"error": "authentication required"}), 401
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

TACHES   = ["jardinage", "bricolage", "courses", "cuisine", "informatique", "garde d'animaux", "déménagement", "autre"]
CRENEAUX = ["matin", "après-midi", "soir", "journée entière"]

@app.route("/apidocs")
def apidocs():
    return render_template("swagger.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/inscription")
def inscription():
    return render_template("inscription.html")

@app.route("/connexion")
def connexion():
    return render_template("connexion.html")

@app.route("/annonces")
@login_required
def annonces():
    return render_template("annonce/liste.html")

@app.route("/annonces/nouvelle")
@login_required
def nouvelle_annonce():
    return render_template("annonce/nouvelle.html")

@app.route("/annonces/<int:id_annonce>")
@login_required
def annonce_detail(id_annonce):
    return render_template("annonce/detail.html")

@app.route("/dispos")
@login_required
def dispos():
    return render_template("dispo/liste.html")

@app.route("/dispos/nouvelle")
@login_required
def nouvelle_dispo():
    return render_template("dispo/nouvelle.html")

@app.route("/dispos/<int:id_dispo>")
@login_required
def dispo_detail(id_dispo):
    return render_template("dispo/detail.html")

@app.route("/profil")
@login_required
def profil():
    return render_template("profil.html")

@app.route("/deconnexion")
def deconnexion():
    session.clear()
    return redirect(url_for("connexion"))

@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    return render_template("admin.html")


# ── API villageois (externe) ──────────────────────────────────────────────────

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


# ── API auth ──────────────────────────────────────────────────────────────────

@app.route("/api/users/me", methods=["GET"])
def api_me():
    if not session.get("id_user"):
        return jsonify({"error": "not authenticated"}), 401
    user = modele.get_user_by_id(session["id_user"])
    if not user:
        return jsonify({"error": "not authenticated"}), 401
    return jsonify({
        "id_user":         user["id_user"],
        "pseudo":          user["pseudo"],
        "email":           user["email"],
        "role":            user["role"],
        "villageois_nom":  user.get("villageois_nom", ""),
        "villageois_photo": user.get("villageois_photo", ""),
    })


@app.route("/api/connexion", methods=["POST"])
def api_connexion():
    data  = request.get_json()
    email = (data.get("email",        "") if data else "")
    mdp   = (data.get("mot_de_passe", "") if data else "")
    user  = modele.verifier_mdp(email, mdp)
    if not user:
        return jsonify({"error": "email ou mot de passe incorrect"}), 401
    session["id_user"] = user["id_user"]
    session["pseudo"]  = user["pseudo"]
    session["role"]    = user["role"]
    return jsonify({"ok": True, "pseudo": user["pseudo"], "role": user["role"]})


@app.route("/api/deconnexion", methods=["POST"])
def api_deconnexion():
    session.clear()
    return jsonify({"ok": True})


@app.route("/api/users", methods=["POST"])
def api_inscription():
    data             = request.get_json()
    pseudo           = (data.get("pseudo",           "") if data else "").strip()[:50]
    email            = (data.get("email",            "") if data else "").strip()[:100]
    mdp              = (data.get("mot_de_passe",     "") if data else "")
    villageois_nom   = (data.get("villageois_nom",   "") if data else "")
    villageois_photo = (data.get("villageois_photo", "") if data else "")
    try:
        user = modele.add_user(pseudo, email, mdp, villageois_nom, villageois_photo)
        session["id_user"] = user["id_user"]
        session["pseudo"]  = user["pseudo"]
        session["role"]    = user["role"]
        return jsonify({"ok": True}), 201
    except Exception:
        return jsonify({"error": "pseudo ou email déjà utilisé"}), 409


# ── API annonces ──────────────────────────────────────────────────────────────

@app.route("/api/annonces", methods=["GET"])
@api_login_required
def api_get_annonces():
    tri = request.args.get("tri", "recent")
    if tri not in ('recent', 'ancien', 'urgence'):
        tri = 'recent'
    return jsonify([to_dict(a) for a in modele.get_all_annonces(tri)])


@app.route("/api/annonces", methods=["POST"])
@api_login_required
def api_create_annonce():
    data        = request.get_json()
    titre       = (data.get("titre",       "") if data else "").strip()[:100]
    description = (data.get("description", "") if data else "").strip()[:2000]
    tache       = (data.get("tache",       "") if data else "")
    if not titre or tache not in TACHES:
        return jsonify({"error": "titre et type de tâche obligatoires"}), 400
    annonce = modele.add_annonce(titre, description, tache, session["id_user"])
    return jsonify(to_dict(annonce)), 201


@app.route("/api/annonces/<int:id_annonce>", methods=["GET"])
@api_login_required
def api_get_annonce(id_annonce):
    annonce = modele.get_annonce_by_id(id_annonce)
    if not annonce:
        return jsonify({"error": "not found"}), 404
    commentaires   = modele.get_commentaires_annonce(id_annonce)
    reactions      = modele.get_reactions_annonce(id_annonce)
    user_reactions = list(modele.get_user_reactions(session["id_user"], id_annonce))
    return jsonify({
        **to_dict(annonce),
        "commentaires":   [to_dict(c) for c in commentaires],
        "reactions":      reactions,
        "user_reactions": user_reactions,
    })


@app.route("/api/annonces/<int:id_annonce>", methods=["DELETE"])
@api_login_required
def api_supprimer_annonce(id_annonce):
    annonce = modele.get_annonce_by_id(id_annonce)
    if not annonce:
        return jsonify({"error": "not found"}), 404
    if annonce["id_user"] != session["id_user"] and session.get("role") != "admin":
        return jsonify({"error": "forbidden"}), 403
    modele.delete_annonce(id_annonce)
    return jsonify({"ok": True})


@app.route("/api/annonces/<int:id_annonce>/reactions/<reaction_type>", methods=["PUT"])
@api_login_required
def api_reagir_annonce(id_annonce, reaction_type):
    if reaction_type not in VALID_REACTION_TYPES:
        return jsonify({"error": "type de réaction invalide"}), 400
    modele.toggle_reaction(session["id_user"], id_annonce, reaction_type)
    return jsonify({"ok": True})


@app.route("/api/annonces/<int:id_annonce>/commentaires", methods=["POST"])
@api_login_required
def api_commenter_annonce(id_annonce):
    data    = request.get_json()
    contenu = (data.get("contenu", "") if data else "").strip()[:1000]
    if not contenu:
        return jsonify({"error": "contenu requis"}), 400
    modele.add_commentaire(contenu, session["id_user"], id_annonce)
    return jsonify({"ok": True})


# ── API dispos ────────────────────────────────────────────────────────────────

@app.route("/api/dispos", methods=["GET"])
@api_login_required
def api_get_dispos():
    dispos_list  = modele.get_all_dispos()
    mes_interets = list(modele.get_user_interets(session["id_user"]))
    return jsonify({
        "dispos":       [to_dict(d) for d in dispos_list],
        "mes_interets": mes_interets,
    })


@app.route("/api/dispos", methods=["POST"])
@api_login_required
def api_create_dispo():
    data        = request.get_json()
    date_dispo  = (data.get("date_dispo",  "") if data else "")
    creneau     = (data.get("creneau",     "") if data else "")
    description = (data.get("description", "") if data else "").strip()[:500]
    if not date_dispo or creneau not in CRENEAUX:
        return jsonify({"error": "date et créneau obligatoires"}), 400
    modele.add_dispo(date_dispo, creneau, description, session["id_user"])
    return jsonify({"ok": True}), 201


@app.route("/api/dispos/<int:id_dispo>", methods=["GET"])
@api_login_required
def api_get_dispo(id_dispo):
    dispo = modele.get_dispo_by_id(id_dispo)
    if not dispo:
        return jsonify({"error": "not found"}), 404
    interets       = modele.get_interets_dispo(id_dispo)
    user_interesse = session["id_user"] in {i["id_user"] for i in interets}
    return jsonify({
        **to_dict(dispo),
        "interets":       [to_dict(i) for i in interets],
        "user_interesse": user_interesse,
    })


@app.route("/api/dispos/<int:id_dispo>", methods=["DELETE"])
@api_login_required
def api_supprimer_dispo(id_dispo):
    dispo = modele.get_dispo_by_id(id_dispo)
    if not dispo:
        return jsonify({"error": "not found"}), 404
    if dispo["id_user"] != session["id_user"] and session.get("role") != "admin":
        return jsonify({"error": "forbidden"}), 403
    modele.delete_dispo(id_dispo)
    return jsonify({"ok": True})


@app.route("/api/dispos/<int:id_dispo>/interet", methods=["PUT"])
@api_login_required
def api_interesse_dispo(id_dispo):
    dispo = modele.get_dispo_by_id(id_dispo)
    if not dispo:
        return jsonify({"error": "not found"}), 404
    if dispo["id_user"] == session["id_user"]:
        return jsonify({"error": "forbidden"}), 403
    modele.toggle_interet(session["id_user"], id_dispo)
    return jsonify({"ok": True})


# ── API users / admin ─────────────────────────────────────────────────────────

@app.route("/api/users", methods=["GET"])
def api_get_users():
    if session.get("role") != "admin":
        return jsonify({"error": "forbidden"}), 403
    return jsonify([to_dict(u) for u in modele.get_all_users()])


@app.route("/api/users/<int:id_user>", methods=["DELETE"])
def api_admin_supprimer_user(id_user):
    if session.get("role") != "admin":
        return jsonify({"error": "forbidden"}), 403
    if id_user == session.get("id_user"):
        return jsonify({"error": "impossible de se supprimer soi-même"}), 400
    modele.delete_user(id_user)
    return jsonify({"ok": True})


@app.route("/api/profil", methods=["PUT"])
@api_login_required
def api_update_profil():
    data           = request.get_json()
    nouveau_pseudo = (data.get("pseudo", "") if data else "").strip()[:50]
    if not nouveau_pseudo:
        return jsonify({"error": "pseudo requis"}), 400
    try:
        modele.update_pseudo(session["id_user"], nouveau_pseudo)
        session["pseudo"] = nouveau_pseudo
        return jsonify({"ok": True, "pseudo": nouveau_pseudo})
    except Exception:
        return jsonify({"error": "ce pseudo est déjà pris"}), 409


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, port=5001)
