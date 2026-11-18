
from app.graph.refactor import propose_refactor_node


def test_propose_refactor_node():

    print("Starting refactor node test...")

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
            "sample.py": "Black exit code: 1\nSTATUS: ISSUES FOUND"
        },
        "refactored_code": {},
        "is_approved": None,
        "reviewer_feedback": None,
        "history": [],
    }

    result = propose_refactor_node(state)

    print("\n========== REFACTORED CODE ==========")

    for filename, code in result["refactored_code"].items():
        print(f"\nFile: {filename}")
        print(code)

    assert "sample.py" in result["refactored_code"]
    assert result["refactored_code"]["sample.py"].strip()
    assert result["history"][-1]["node"] == "propose_refactor_node"

    print("\nSUCCESS: propose_refactor_node working!")


if __name__ == "__main__":
    test_propose_refactor_node()
