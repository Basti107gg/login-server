import json
import requests

GITHUB_REPO = "Basti107gg/login-server"
FILE_PATH = "accounts.json"
TOKEN = "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"

def upload(data):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"

    content = json.dumps(data, indent=4)

    r = requests.put(
        url,
        headers={
            "Authorization": f"token {TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        },
        json={
            "message": "update accounts",
            "content": content.encode().decode("utf-8")
        }
    )

    print(r.status_code, r.text)

upload({"Basti": "29a10C00"})
