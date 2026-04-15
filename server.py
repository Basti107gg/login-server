from flask import Flask, request, jsonify
import json
import os
import requests
import base64

app = Flask(__name__)

DB_FILE = "accounts.json"

# =========================
# LOKALE ACCOUNTS
# =========================
def load_accounts():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)

    with open(DB_FILE, "r") as f:
        return json.load(f)

# =========================
# GITHUB ACCOUNTS (READ ONLY)
# =========================
GITHUB_TOKEN = "DEIN_TOKEN"
GITHUB_REPO = "USERNAME/REPO"
GITHUB_FILE = "accounts.json"

def load_github_accounts():
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"

        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return {}

        data = r.json()
        content = base64.b64decode(data["content"]).decode("utf-8")
        return json.loads(content)

    except:
        return {}

# =========================
# LOGIN (LOKAL + GITHUB)
# =========================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = data.get("username")
    pw = data.get("password")

    local = load_accounts()
    github = load_github_accounts()

    accounts = {**local, **github}

    if user in accounts and accounts[user] == pw:
        return jsonify({"status": "ok"})

    return jsonify({"status": "error"})

# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
