from unittest.mock import patch

from app.graph.nodes import apply_changes_node


test_state = {
    "pr_url": "https://github.com/aayushgaurav/code-review-agent-demo/pull/1",
    "code_contents": {},
    "lint_errors": {},
    "refactored_code": {
        "sample.py": "print('Hello World')\n"
    },
    "is_approved": True,
    "reviewer_feedback": None,
    "history": [],
}

mock_result = [
    {
        "file": "sample.py",
        "commit_sha": "mock_commit_123",
        "commit_url": "https://github.com/mock/commit/123",
    }
]

with patch(
    "app.graph.nodes.apply_refactored_code",
    return_value=mock_result,
) as mock_commit:

    result = apply_changes_node(test_state)

    mock_commit.assert_called_once()

    print("SUCCESS: Approved changes reached commit function!")
    print("Commit function called:", mock_commit.call_count)
    print("Node result:", result)