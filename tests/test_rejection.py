from unittest.mock import patch

from app.graph.nodes import apply_changes_node


def test_rejected_changes_are_not_committed():

    state = {
        "pr_url": "https://github.com/aayushgaurav/code-review-agent-demo/pull/1",
        "code_contents": {
            "sample.py": "print('original')"
        },
        "lint_errors": {},
        "refactored_code": {
            "sample.py": "print('refactored')"
        },
        "is_approved": False,
        "reviewer_feedback": "Please fix the logic.",
        "history": [],
    }

    with patch(
        "app.graph.nodes.apply_refactored_code"
    ) as mock_commit:

        result = apply_changes_node(state)

    mock_commit.assert_not_called()

    assert result["history"][-1]["status"] == "rejected"

    print("SUCCESS: Rejected changes were not committed!")