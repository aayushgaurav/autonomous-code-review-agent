
from unittest.mock import MagicMock, patch

from app.graph.refactor import propose_refactor_node


def test_refactor_node_uses_lint_errors_and_reviewer_feedback():
    state = {
        "pr_url": "https://github.com/aayushgaurav/code-review-agent-demo/pull/1",
        "code_contents": {
            "sample.py": "def add(a,b):\n return a+b"
        },
        "lint_errors": {
            "sample.py": "E231 missing whitespace after ','"
        },
        "refactored_code": {},
        "is_approved": None,
        "reviewer_feedback": "Use proper formatting.",
        "history": [],
    }

    mock_response = MagicMock()
    mock_response.content = "def add(a, b):\n    return a + b"

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = mock_response

    with patch("app.graph.refactor.ChatOpenAI", return_value=mock_llm):
        result = propose_refactor_node(state)

    assert result["refactored_code"]["sample.py"] == mock_response.content
    assert result["is_approved"] is None
    assert result["history"][-1]["mode"] == "llm"

    prompt = mock_llm.invoke.call_args[0][0]
    assert "E231" in prompt
    assert "Use proper formatting." in prompt
