
from app.graph.refactor import propose_refactor_node
from app.tools.sandbox_tool import run_linter_tool


def test_validate_refactor():

    state = {
        "pr_url": "https://github.com/aayushgaurav/code-review-agent-demo/pull/1",
        "code_contents": {
            "sample.py": (
                "def calculate_total(price, quantity):\n"
                "    total = price * quantity\n"
                "    return total\n"
            )
        },
        "lint_errors": {
            "sample.py": "Black exit code: 1"
        },
        "refactored_code": {},
        "is_approved": None,
        "reviewer_feedback": None,
        "history": [],
    }

    # Generate refactored code
    result = propose_refactor_node(state)

    corrected_code = result["refactored_code"]["sample.py"]
    print("\n========== GENERATED CODE ==========\n")
    print(repr(corrected_code))

    # Run Flake8 and Black again
    lint_result = run_linter_tool.invoke({
        "code_string": corrected_code
    })

    print("\n========== RE-VALIDATION RESULTS ==========")
    print(lint_result)

    assert "STATUS: PASSED" in lint_result

    print("\nSUCCESS: Refactored code passed validation!")


if __name__ == "__main__":
    test_validate_refactor()
