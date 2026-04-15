from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)

# =========================
# DATEI
# =========================
DB_FILE = "accounts.json"

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
# LOGIN API
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
# LOGIN SEITE (ADMIN LOGIN)
# =========================
ADMIN_PASSWORD = "29a10C00"

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        if request.form.get("admin") == ADMIN_PASSWORD:
            return """
            <h2>Login OK</h2>
            <a href='/admin'>Go Admin Panel</a>
            """
        return "Wrong password", 403

    return """
    <h1>LOGIN</h1>
    <form method="post">
        <input name="admin" placeholder="Admin Passwort">
        <button>Login</button>
    </form>
    """

# =========================
# ACCOUNT ERSTELLEN SEITE
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():
    accounts = load_accounts()

    if request.method == "POST":
        user = request.form.get("user")
        pw = request.form.get("pw")

        if user and pw:
            accounts[user] = pw
            save_accounts(accounts)
            return "<h2>Account erstellt!</h2><a href='/register'>Zurück</a>"

    return """
    <h1>ACCOUNT ERSTELLEN</h1>

    <form method="post">
        <input name="user" placeholder="Username"><br><br>
        <input name="pw" placeholder="Password"><br><br>
        <button>Create</button>
    </form>

    <br>
    <a href='/login'>Admin Login</a>
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
    <a href="/register">Account erstellen</a>
    """, accounts=accounts)

# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
