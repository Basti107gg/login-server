# server.py
from flask import Flask, request, jsonify, render_template_string, redirect
import json
import os
import shutil
import time

app = Flask(__name__)

DB_FILE = "accounts.json"
BACKUP_FILE = "accounts_backup.json"

ADMIN_PASSWORD = "29a10C00"

# =========================
# LOAD / SAVE
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
            with open(BACKUP_FILE, "r") as f:
                return json.load(f)
        return {}

def save_accounts(data):
    if os.path.exists(DB_FILE):
        shutil.copy(DB_FILE, BACKUP_FILE)

    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)
        f.flush()
        os.fsync(f.fileno())

# =========================
# LOGIN (MIT IP TRACKING)
# =========================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = data.get("username")
    pw = data.get("password")

    accounts = load_accounts()

    if user in accounts and accounts[user]["password"] == pw:
        ip = request.remote_addr
        now = int(time.time())

        # neue IP hinzufügen oder updaten
        if ip not in accounts[user]["ips"]:
            accounts[user]["ips"][ip] = now
        else:
            accounts[user]["ips"][ip] = now

        save_accounts(accounts)

        return jsonify({"status": "ok"})

    return jsonify({"status": "error"})

# =========================
# ADMIN LOGIN
# =========================
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            return redirect("/admin")
        return "❌ Falsches Passwort"

    return """
    <h2>🔒 Admin Login</h2>
    <form method="post">
        <input type="password" name="password">
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
            accounts[user] = {
                "password": pw,
                "ips": {}
            }
            save_accounts(accounts)

    # DELETE
    if request.method == "POST" and "delete" in request.form:
        user = request.form.get("delete")
        if user in accounts:
            del accounts[user]
            save_accounts(accounts)

    now = int(time.time())

    return render_template_string("""
    <h1>ADMIN PANEL</h1>

    <h2>➕ Account erstellen</h2>
    <form method="post">
        <input name="username"><br><br>
        <input name="password"><br><br>
        <button name="create">Erstellen</button>
    </form>

    <hr>

    <h2>🗑 Account löschen</h2>
    <form method="post">
        <input name="delete">
        <button>Löschen</button>
    </form>

    <hr>

    <h2>📦 Accounts</h2>

    <ul>
    {% for user, data in accounts.items() %}
        <li onclick="toggle('{{user}}')" style="cursor:pointer;">
            <b>{{user}}</b>
            <div id="{{user}}" style="display:none; margin-left:20px;">
                Passwort: {{data.password}}<br>
                IPs:<br>
                {% for ip, last in data.ips.items() %}
                    {% if now - last < 120 %}
                        🟢 {{ip}} (aktiv)
                    {% else %}
                        ⚪ {{ip}}
                    {% endif %}
                    <br>
                {% endfor %}
            </div>
        </li>
    {% endfor %}
    </ul>

    <script>
    function toggle(user){
        let el = document.getElementById(user);
        el.style.display = (el.style.display === "none") ? "block" : "none";
    }
    </script>
    """, accounts=accounts, now=now)

# =========================
# HOME REDIRECT
# =========================
@app.route("/")
def home():
    return redirect("/admin-login")

# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
