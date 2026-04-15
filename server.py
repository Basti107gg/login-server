from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)

# =========================
# LOCAL DATABASE
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
def login():
    data = request.json
    user = data.get("username")
    pw = data.get("password")

    accounts = load_accounts()

    if user in accounts and accounts[user] == pw:
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error"})

# =========================
# ADMIN PANEL
# =========================
@app.route("/", methods=["GET", "POST"])
def admin():
    accounts = load_accounts()

    if request.method == "POST":
        user = request.form.get("username")
        pw = request.form.get("password")

        if user and pw:
            accounts[user] = pw
            save_accounts(accounts)

        # DELETE (optional simple fix)
        delete_user = request.form.get("delete")
        if delete_user:
            if delete_user in accounts:
                del accounts[delete_user]
                save_accounts(accounts)

    return render_template_string("""
    <h1>ADMIN PANEL</h1>

    <h2>Create Account</h2>
    <form method="post">
        <input name="username" placeholder="Username"><br><br>
        <input name="password" placeholder="Password"><br><br>
        <button>Create</button>
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
    {% for user in accounts %}
        <li>{{user}} : {{accounts[user]}}</li>
    {% endfor %}
    </ul>
    """, accounts=accounts)

# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
