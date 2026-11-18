from app.graph.nodes import lint_code_node


def test_lint_code_node():

    state = {
        "pr_url": "https://github.com/aayushgaurav/code-review-agent-demo/pull/1",
        "code_contents": {
            "sample.py": """
def calculate_total(price, quantity):
    total = price * quantity
    return total
"""
        },
        "lint_errors": {},
        "refactored_code": {},
        "is_approved": None,
        "reviewer_feedback": None,
        "history": [],
    }

    result = lint_code_node(state)

    print("\n========== LINT RESULTS ==========")

    for filename, output in result["lint_errors"].items():
        print(f"\nFile: {filename}")
        print(output)

    assert "sample.py" in result["lint_errors"]
    assert "lint_code_node" == result["history"][-1]["node"]

    print("\nSUCCESS: lint_code_node working!")


if __name__ == "__main__":
    test_lint_code_node()