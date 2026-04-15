# server.py
from flask import Flask, request, jsonify, render_template_string, redirect, session
import json
import os
import shutil

app = Flask(__name__)
app.secret_key = "super_secret_key_123"  # wichtig für Login Session

ADMIN_PASSWORD = "29a10C00"

# =========================
# STORAGE PATH
# =========================
if os.path.exists("/data"):
    DB_FILE = "/data/accounts.json"
    BACKUP_FILE = "/data/accounts_backup.json"
else:
    DB_FILE = "accounts.json"
    BACKUP_FILE = "accounts_backup.json"

# =========================
# LOAD ACCOUNTS
# =========================
def load_accounts():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)

    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        if os.path.exists(BACKUP_FILE):
            shutil.copy(BACKUP_FILE, DB_FILE)
            with open(DB_FILE, "r") as f:
                return json.load(f)
        return {}

# =========================
# SAVE ACCOUNTS
# =========================
def save_accounts(data):
    if os.path.exists(DB_FILE):
        shutil.copy(DB_FILE, BACKUP_FILE)

    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)
        f.flush()
        os.fsync(f.fileno())

# =========================
# LOGIN API (für deine Programme)
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
            session["admin"] = True
            return redirect("/")
        else:
            return render_template_string("""
            <h2>Login falsch!</h2>
            <a href="/admin-login">Zurück</a>
            """)

    return render_template_string("""
    <h2>🔐 Admin Login</h2>
    <form method="post">
        <input name="password" type="password" placeholder="Passwort"><br><br>
        <button>Login</button>
    </form>
    """)

# =========================
# ADMIN PANEL (GESCHÜTZT)
# =========================
@app.route("/", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        return redirect("/admin-login")

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

    <a href="/logout">Logout</a>

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

    <h2>📦 Accounts</h2>
    <ul>
    {% for user in accounts %}
        <li>{{user}} : {{accounts[user]}}</li>
    {% endfor %}
    </ul>
    """, accounts=accounts)

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin-login")

# =========================
# START SERVER
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
