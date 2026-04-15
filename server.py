from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)

DB_FILE = "accounts.json"

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
        return {}

def save_accounts(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================
# LOGIN API (für dein Programm)
# =========================
@app.route("/login", methods=["POST"])
def login_api():
    data = request.json
    user = data.get("username")
    pw = data.get("password")

    accounts = load_accounts()

    if user in accounts and accounts[user] == pw:
        return jsonify({"status": "ok"})

    return jsonify({"status": "error"})

# =========================
# ADMIN LOGIN SEITE
# =========================
ADMIN_PASSWORD = "29a10C00"

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            return "<h2>Login OK</h2><a href='/admin'>Go Admin Panel</a>"
        return "Wrong password", 403

    return """
    <h1>ADMIN LOGIN</h1>
    <form method="post">
        <input name="password" placeholder="Admin Passwort">
        <button>Login</button>
    </form>
    """

# =========================
# ADMIN PANEL
# =========================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    accounts = load_accounts()

    if request.method == "POST":
        if request.form.get("admin") != ADMIN_PASSWORD:
            return "Wrong password", 403

        if "create" in request.form:
            user = request.form.get("user")
            pw = request.form.get("pw")

            if user and pw:
                accounts[user] = pw
                save_accounts(accounts)

        if "delete" in request.form:
            user = request.form.get("delete")
            if user in accounts:
                del accounts[user]
                save_accounts(accounts)

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

    <br>
    <a href="/admin-login">Back</a>
    """, accounts=accounts)

# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
