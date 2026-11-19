import os
import json
import hmac
import hashlib
import requests

from dotenv import load_dotenv

load_dotenv()

secret = os.getenv("GITHUB_WEBHOOK_SECRET")

payload = {
    "action": "opened",
    "repository": {
        "full_name": "aayushgaurav/code-review-agent-demo"
    },
    "pull_request": {
        "number": 1,
        "html_url": "https://github.com/aayushgaurav/code-review-agent-demo/pull/1"
    }
}

body = json.dumps(payload).encode("utf-8")

signature = "sha256=" + hmac.new(
    secret.encode("utf-8"),
    body,
    hashlib.sha256
).hexdigest()

response = requests.post(
    "http://localhost:8000/api/webhooks/github",
    data=body,
    headers={
        "X-Hub-Signature-256": signature,
        "Content-Type": "application/json"
    },
    timeout=300
)

print("Status:", response.status_code)
print("Response:", response.text)