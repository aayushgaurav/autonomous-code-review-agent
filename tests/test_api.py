
import os
import hmac
import hashlib
import json

from fastapi.testclient import TestClient
from unittest.mock import patch

from app.api.main import app

client = TestClient(app)


def test_github_webhook():
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
    assert response.json()["thread_id"] == (
        "github-aayushgaurav-code-review-agent-demo-pr-1"
    )
    mocked_invoke.assert_called_once()

    print("SUCCESS: GitHub webhook endpoint test passed!")



def test_approval_endpoint():
    thread_id = "github-test-repo-pr-1"
    api_key = "test-review-key"

    mock_snapshot = type(
        "MockSnapshot",
        (),
        {
            "values": {"pr_url": "https://github.com/test/repo/pull/1"},
            "next": ("apply_changes_node",),
        },
    )()

    with patch("app.api.main.REVIEW_API_KEY", api_key):
        with patch(
            "app.graph.workflow.graph.get_state",
            return_value=mock_snapshot,
        ):
            with patch(
                "app.graph.workflow.graph.update_state"
            ) as mocked_update:
                with patch(
                    "app.graph.workflow.graph.invoke"
                ) as mocked_invoke:

                    response = client.post(
                        f"/api/reviews/{thread_id}/approve",
                        json={
                            "approved": False,
                            "feedback": "Please fix the formatting.",
                        },
                        headers={"X-API-Key": api_key},
                    )

    assert response.status_code == 200
    assert response.json()["approved"] is False

    mocked_update.assert_called_once()
    mocked_invoke.assert_called_once()

    print("SUCCESS: Authenticated approval/rejection test passed!")




def test_github_webhook_rejects_invalid_signature():
    os.environ["GITHUB_WEBHOOK_SECRET"] = "test_secret"

    response = client.post(
        "/api/webhooks/github",
        content=b'{"action":"opened"}',
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=invalid_signature",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid GitHub webhook signature."

    print("SUCCESS: Invalid webhook signature rejected!")


def test_approval_endpoint_rejects_invalid_api_key():
    with patch("app.api.main.REVIEW_API_KEY", "correct-test-key"):
        response = client.post(
            "/api/reviews/test-thread/approve",
            json={
                "approved": False,
                "feedback": "Test feedback",
            },
            headers={"X-API-Key": "wrong-key"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key."

    print("SUCCESS: Invalid API key rejected!")

 