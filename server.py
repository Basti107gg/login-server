# server.py
from flask import Flask, request, jsonify, render_template_string, redirect
import json
import os
import shutil

app = Flask(__name__)

DB_FILE = "accounts.json"
BACKUP_FILE = "accounts_backup.json"

ADMIN_PASSWORD = "29a10C00"

# =========================
# LOAD ACCOUNTS (MIT BACKUP)
# =========================
def load_accounts():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)

    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        # Falls kaputt → Backup laden
        if os.path.exists(BACKUP_FILE):
            with open(BACKUP_FILE, "r") as f:
                return json.load(f)
        return {}

# =========================
# SAVE ACCOUNTS (MIT BACKUP)
# =========================
def save_accounts(data):
    # Backup erstellen
    if os.path.exists(DB_FILE):
        shutil.copy(DB_FILE, BACKUP_FILE)

    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)
        f.flush()
        os.fsync(f.fileno())

# =========================
# LOGIN API (für Programme)
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
# ADMIN LOGIN PAGE
# =========================
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        pw = request.form.get("password")

        if pw == ADMIN_PASSWORD:
            return redirect("/admin")
        else:
            return "❌ Falsches Passwort!"

    return """
    <h2>🔒 Admin Login</h2>
    <form method="post">
        <input type="password" name="password" placeholder="Passwort"><br><br>
        <button>Login</button>
    </form>
    """

# =========================
# ADMIN PANEL
# =========================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    accounts = load_accounts()

    # CREATE
    if request.method == "POST" and "create" in request.form:
        user = request.form.get("username")
        pw = request.form.get("password")

        if user and pw:
            accounts[user] = pw
            save_accounts(accounts)

    # DELETE
    if request.method == "POST" and "delete" in request.form:
        user = request.form.get("delete")
        if user in accounts:
            del accounts[user]
            save_accounts(accounts)

    return render_template_string("""
    <h1>ADMIN PANEL</h1>

    <h2>➕ Account erstellen</h2>
    <form method="post">
        <input name="username" placeholder="Username"><br><br>
        <input name="password" placeholder="Password"><br><br>
        <button name="create">Erstellen</button>
    </form>

    <hr>

    <h2>🗑 Account löschen</h2>
    <form method="post">
        <input name="delete" placeholder="Username">
        <button>Löschen</button>
    </form>

    <hr>

    <h2>📦 Accounts </h2>

    <ul>
    {% for user in accounts %}
        <li onclick="toggle('{{user}}')" style="cursor:pointer;">
            {{user}} :
            <span id="{{user}}" style="display:none;">{{accounts[user]}}</span>
            <span id="hidden_{{user}}">********</span>
        </li>
    {% endfor %}
    </ul>

    <script>
    function toggle(user){
        let pw = document.getElementById(user);
        let hidden = document.getElementById("hidden_" + user);

        if(pw.style.display === "none"){
            pw.style.display = "inline";
            hidden.style.display = "none";
        } else {
            pw.style.display = "none";
            hidden.style.display = "inline";
        }
    }
    </script>
    """, accounts=accounts)

# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
