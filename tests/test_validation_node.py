from unittest.mock import MagicMock, patch

from app.graph.nodes import (
    validate_refactor_node,
    validation_decision_router,
)


def sample_state():
    return {
        "pr_url": "https://github.com/aayushgaurav/code-review-agent-demo/pull/1",
        "code_contents": {"sample.py": "original code"},
        "lint_errors": {},
        "refactored_code": {
            "sample.py": "def add(a, b):\n    return a + b\n"
        },
        "validation_passed": None,
        "is_approved": None,
        "reviewer_feedback": None,
        "history": [],
    }


def test_validation_passes():
    state = sample_state()
    mock_tool = MagicMock()
    mock_tool.invoke.return_value = "STATUS: PASSED"

    with patch("app.graph.nodes.run_linter_tool", mock_tool):
        result = validate_refactor_node(state)

    assert result["validation_passed"] is True
    assert validation_decision_router(result) == "review"


def test_validation_failure_routes_to_refactor():
    state = sample_state()
    mock_tool = MagicMock()
    mock_tool.invoke.return_value = "STATUS: ISSUES FOUND"

    with patch("app.graph.nodes.run_linter_tool", mock_tool):
        result = validate_refactor_node(state)

    assert result["validation_passed"] is False
    assert validation_decision_router(result) == "refactor"