import json
import requests

GITHUB_API = "https://api.github.com/repos/Basti107gg/login-server/contents/accounts.json"
TOKEN = "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"

def upload(data):
    content = json.dumps(data, indent=4).encode().decode("utf-8")

    r = requests.put(
        GITHUB_API,
        headers={
            "Authorization": f"token {TOKEN}"
        },
        json={
            "message": "update accounts",
            "content": content.encode().decode("utf-8")
        }
    )

    print(r.text)

# example
upload({"user": "pass"})
