from flask import Flask, request, jsonify
import json
import os
import requests
import base64

app = Flask(__name__)

# =========================
# LOKALE DATEI
# =========================
DB_FILE = "accounts.json"

def load_local():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)

    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_local(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================
# GITHUB CONFIG (WICHTIG ANPASSEN)
# =========================
GITHUB_REPO = "Basti107gg/login-server"
GITHUB_FILE = "accounts.json"
GITHUB_TOKEN = "DEIN_TOKEN_HIER"  # nur nötig wenn schreiben, lesen geht ohne

# =========================
# GITHUB LOAD (READ ONLY)
# =========================
def load_github():
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"

        r = requests.get(url, headers={
            "Accept": "application/vnd.github.v3+json"
        })

        if r.status_code != 200:
            return {}

        data = r.json()
        content = base64.b64decode(data["content"]).decode("utf-8")
        return json.loads(content)

    except:
        return {}

# =========================
# MERGE ACCOUNTS
# =========================
def load_accounts():
    local = load_local()
    github = load_github()

    merged = github.copy()
    merged.update(local)
    return merged

# =========================
# LOGIN
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
# ADMIN (CREATE + DELETE)
# =========================
ADMIN_PASSWORD = "29a10C00"

@app.route("/", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("admin") != ADMIN_PASSWORD:
            return "Wrong password", 403

        accounts = load_local()

        if "create" in request.form:
            u = request.form.get("user")
            p = request.form.get("pw")
            accounts[u] = p
            save_local(accounts)

        if "delete" in request.form:
            u = request.form.get("delete")
            if u in accounts:
                del accounts[u]
                save_local(accounts)

    accounts = load_accounts()

    html = """
    <h1>ADMIN PANEL</h1>

    <form method="post">
        <input name="admin" placeholder="Admin Passwort">
        <button>Login</button>
    </form>

    <hr>

    <h3>Create</h3>
    <form method="post">
        <input name="user" placeholder="User">
        <input name="pw" placeholder="Pass">
        <button name="create">Add</button>
    </form>

    <h3>Delete</h3>
    <form method="post">
        <input name="delete" placeholder="User">
        <button>Delete</button>
    </form>

    <hr>

    <h3>Accounts</h3>
    {% for u in accounts %}
        <p>{{u}} : {{accounts[u]}}</p>
    {% endfor %}
    """

    from flask import render_template_string
    return render_template_string(html, accounts=accounts)

# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
