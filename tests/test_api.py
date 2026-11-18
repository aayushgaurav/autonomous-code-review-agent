from fastapi.testclient import TestClient
from unittest.mock import patch

from app.api.main import app


client = TestClient(app)


def test_github_webhook():
    mock_graph = patch(
        "app.graph.workflow.graph.invoke"
    )

    with mock_graph as mocked_invoke:
        response = client.post(
            "/api/webhooks/github",
            json={
                "action": "opened",
                "pull_request": {
                    "html_url": "https://github.com/aayushgaurav/code-review-agent-demo/pull/1",
                    "number": 1,
                },
                "repository": {
                    "full_name": "aayushgaurav/code-review-agent-demo"
                },
            },
        )

    assert response.status_code == 200
    assert response.json()["message"] == "Code review started."
    assert response.json()["thread_id"] == (
        "github-aayushgaurav/code-review-agent-demo-pr-1"
    )
    mocked_invoke.assert_called_once()

    print("SUCCESS: GitHub webhook endpoint test passed!")



def test_approval_endpoint():
    thread_id = "github-test-repo-pr-1"

    mock_snapshot = type(
        "MockSnapshot",
        (),
        {
            "values": {"pr_url": "https://github.com/test/repo/pull/1"},
            "next": ("apply_changes_node",),
        },
    )()

    with patch("app.graph.workflow.graph.get_state", return_value=mock_snapshot):
        with patch("app.graph.workflow.graph.update_state") as mocked_update:
            with patch("app.graph.workflow.graph.invoke") as mocked_invoke:

                response = client.post(
                    f"/api/reviews/{thread_id}/approve",
                    json={
                        "approved": False,
                        "feedback": "Please fix the formatting.",
                    },
                )

    assert response.status_code == 200
    assert response.json()["approved"] is False

    mocked_update.assert_called_once()
    mocked_invoke.assert_called_once()

    print("SUCCESS: Approval/rejection endpoint test passed!")