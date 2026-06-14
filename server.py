from flask import Flask, request
import requests, json
from datetime import date, timedelta
import base64
import os

# -----------------------------
# CONFIG GITHUB
# -----------------------------
GITHUB_TOKEN = "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"  # ⚠️ Mets ton token GitHub ici
REPO = "vivisua1/renommeur-licences"
FILE_PATH = "licences.json"

ADMIN_PASSWORD = "V-ADMIN-2026"

app = Flask(__name__)

# -----------------------------
# CHARGER LA PAGE HTML
# -----------------------------
with open("activation.html", "r", encoding="utf-8") as f:
    HTML = f.read()

# -----------------------------
# AJOUT AUTOMATIQUE D’UNE LICENCE (EXPIRATION 30 JOURS)
# -----------------------------
def add_licence(key, email):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

    # Récupérer le fichier actuel
    r = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    data = r.json()

    # Télécharger le JSON actuel
    content = json.loads(requests.get(data["download_url"]).text)

    # Ajouter la licence
    content[key] = {
        "email": email,
        "expires": str(date.today() + timedelta(days=30))
    }

    # Encoder en base64 (GitHub API)
    new_content = json.dumps(content, indent=4)
    encoded = base64.b64encode(new_content.encode()).decode()

    # Commit sur GitHub
    requests.put(
        url,
        headers={"Authorization": f"token {GITHUB_TOKEN}"},
        json={
            "message": f"Add licence {key}",
            "content": encoded,
            "sha": data["sha"]
        }
    )

# -----------------------------
# ROUTE : Page d’accueil
# -----------------------------
@app.route("/", methods=["GET"])
def home():
    return HTML

# -----------------------------
# ROUTE : Activation
# -----------------------------
@app.route("/activate", methods=["POST"])
def activate():
    email = request.form["email"]
    key = request.form["key"]

    add_licence(key, email)

    return f"""
    <h2>Licence activée !</h2>
    <p>Email : {email}</p>
    <p>Clé : {key}</p>
    <p>Expiration : {str(date.today() + timedelta(days=30))}</p>
    """

# -----------------------------
# ROUTE : Dashboard admin
# -----------------------------
@app.route("/admin")
def admin():
    pwd = request.args.get("pwd", "")
    if pwd != ADMIN_PASSWORD:
        return "<h3>Accès refusé</h3>"

   url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}?ref=main"
    data = requests.get(url).json()

    html = "<h2>Dashboard Licences</h2><ul>"
    for key, info in data.items():
        html += f"<li><b>{key}</b> — {info['email']} — expire : {info['expires']}</li>"
    html += "</ul>"

    return html

# -----------------------------
# LANCEMENT LOCAL / RENDER
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
