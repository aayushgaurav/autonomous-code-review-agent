def test_github_webhook():
    import os
    import hmac
    import hashlib
    import json

    secret = "test_secret"
    os.environ["GITHUB_WEBHOOK_SECRET"] = secret

    payload = {
        "action": "opened",
        "pull_request": {
            "html_url": "https://github.com/aayushgaurav/code-review-agent-demo/pull/1",
            "number": 1,
        },
        "repository": {
            "full_name": "aayushgaurav/code-review-agent-demo"
        },
    }

    body = json.dumps(payload).encode("utf-8")

    signature = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    with patch("app.graph.workflow.graph.invoke") as mocked_invoke:
        response = client.post(
            "/api/webhooks/github",
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": signature,
            },
        )

    assert response.status_code == 200
    assert response.json()["message"] == "Code review started."
    mocked_invoke.assert_called_once()
