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
        json.dump(data, f)

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

@app.route("/", methods=["GET", "POST"])
def admin():
    accounts = load_accounts()

    if request.method == "POST":
        user = request.form.get("username")
        pw = request.form.get("password")

        accounts[user] = pw
        save_accounts(accounts)

    return render_template_string("""
    <h2>Account erstellen</h2>
    <form method="post">
        Username: <input name="username"><br><br>
        Passwort: <input name="password"><br><br>
        <button>Erstellen</button>
    </form>
    <hr>
    <h3>Accounts:</h3>
    {{accounts}}
    """, accounts=accounts)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)