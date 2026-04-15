from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)

DB_FILE = "accounts.json"

def load_accounts():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)

    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_accounts(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================
# LOGIN API
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
@app.route("/", methods=["GET", "POST"])
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
    <html>
    <head>
    <script>
        function togglePassword(user) {
            let el = document.getElementById("pw_" + user);
            if (el.style.display === "none") {
                el.style.display = "block";
            } else {
                el.style.display = "none";
            }
        }
    </script>
    </head>

    <body>
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
    {% for user, pw in accounts.items() %}
        <li>
            <b onclick="togglePassword('{{user}}')" style="cursor:pointer;color:blue;">
                {{user}}
            </b>

            <div id="pw_{{user}}" style="display:none;margin-left:20px;">
                🔑 Passwort: {{pw}}
            </div>
        </li>
    {% endfor %}
    </ul>

    </body>
    </html>
    """, accounts=accounts)

# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
