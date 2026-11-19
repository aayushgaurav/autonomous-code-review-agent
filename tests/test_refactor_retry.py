from unittest.mock import MagicMock, patch

from app.graph.refactor import propose_refactor_node


def test_refactor_uses_previous_generated_code():
    state = {
        "pr_url": "https://github.com/aayushgaurav/code-review-agent-demo/pull/1",
        "code_contents": {
            "sample.py": "def add(a,b): return a+b\n"
        },
        "lint_errors": {
            "sample.py": "STATUS: ISSUES FOUND"
        },
        "refactored_code": {
            "sample.py": "def add(a, b):\n    return a + b\n"
        },
        "validation_passed": False,
        "is_approved": None,
        "reviewer_feedback": None,
        "history": [],
    }

    mock_response = MagicMock()
    mock_response.content = "def add(a, b):\n    return a + b\n"

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = mock_response

    with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
        with patch(
            "app.graph.refactor.ChatOpenAI",
            return_value=mock_llm,
        ):
            result = propose_refactor_node(state)

    prompt = mock_llm.invoke.call_args[0][0]

    assert "CURRENT CODE TO FIX:" in prompt
    assert "def add(a, b):\n    return a + b" in prompt
    assert "ORIGINAL CODE (REFERENCE):" in prompt
    assert "refactored_code" in result