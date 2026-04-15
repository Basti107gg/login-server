from flask import Flask, request, jsonify, render_template_string
import json
import os
import requests

app = Flask(__name__)

# =========================
# LOKALE DATEI (SICHER + DAUERHAFT)
# =========================
DB_FILE = "accounts.json"

def load_local():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)

    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_local(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================
# GITHUB (PUBLIC READ ONLY)
# =========================
GITHUB_USER = "Basti107gg"
GITHUB_REPO = "login-server"
GITHUB_FILE = "accounts.json"

def load_github():
    try:
        url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{GITHUB_FILE}"
        r = requests.get(url, timeout=5)

        if r.status_code == 200:
            return r.json()

    except:
        pass

    return {}

# =========================
# ACCOUNTS MERGE (GITHUB + LOKAL)
# =========================
def load_accounts():
    local = load_local()
    github = load_github()

    merged = github.copy()
    merged.update(local)
    return merged

# =========================
# LOGIN SYSTEM
# =========================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = data.get("username")
    pw = data.get("password")

    accounts = load_accounts()

    if user in accounts and accounts[user] == pw:
        return jsonify({"status": "ok"})

    return jsonify({"status": "error"})

# =========================
# ADMIN PANEL
# =========================
ADMIN_PASSWORD = "29a10C00"

@app.route("/", methods=["GET", "POST"])
def admin():
    accounts = load_accounts()

    # Admin check
    if request.method == "POST":
        if request.form.get("admin") != ADMIN_PASSWORD:
            return "Wrong password", 403

        local = load_local()

        # CREATE ACCOUNT
        if "create" in request.form:
            user = request.form.get("user")
            pw = request.form.get("pw")

            if user and pw:
                local[user] = pw
                save_local(local)

        # DELETE ACCOUNT
        if "delete" in request.form:
            user = request.form.get("delete")

            if user in local:
                del local[user]
                save_local(local)

    accounts = load_accounts()

    return render_template_string("""
    <h1>ADMIN PANEL</h1>

    <form method="post">
        <input name="admin" placeholder="Admin Passwort">
        <button>Login</button>
    </form>

    <hr>

    <h2>Create Account</h2>
    <form method="post">
        <input name="user" placeholder="Username">
        <input name="pw" placeholder="Password">
        <button name="create">Create</button>
    </form>

    <h2>Delete Account</h2>
    <form method="post">
        <input name="delete" placeholder="Username">
        <button>Delete</button>
    </form>

    <hr>

    <h2>Accounts</h2>
    <ul>
    {% for u in accounts %}
        <li>{{u}} : {{accounts[u]}}</li>
    {% endfor %}
    </ul>
    """, accounts=accounts)

# =========================
# START SERVER
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
