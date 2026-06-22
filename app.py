from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_cors import CORS
import modele
import requests as req

app = Flask(__name__)
app.secret_key = "sos-villageois-secret"
CORS(app)

modele.init_db()

# * routes a venir :
# auth : /inscription, /connexion, /deconnexion
# villageois : /api/villageois (nookipedia)
# annonces : /annonces, /annonces/<id>, /annonces/nouvelle, ...
# disponibilites, commentaires, reactions, interets...

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
