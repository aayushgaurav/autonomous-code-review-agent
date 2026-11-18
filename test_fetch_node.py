from app.graph.nodes import fetch_pr_node
from app.tools.sandbox_tool import run_linter_tool

def test_fetch_pr_node():

    state = {
        "pr_url": "https://github.com/aayushgaurav/code-review-agent-demo/pull/1",
        "code_contents": {},
        "lint_errors": {},
        "refactored_code": {},
        "is_approved": None,
        "reviewer_feedback": None,
        "history": [],
    }

    result = fetch_pr_node(state)

    print("\nFetched files:")
    for filename, code in result["code_contents"].items():
        print(f"\nFile: {filename}")
        print(code)

    assert result["code_contents"]
    assert "fetch_pr_node" == result["history"][-1]["node"]

    print("\nSUCCESS: fetch_pr_node working!")


if __name__ == "__main__":
    test_fetch_pr_node()



def lint_code_node(state: ReviewState) -> dict:
    """
    Run Flake8 and Black on every fetched Python file.
    """

    code_contents = state.get("code_contents", {})

    if not code_contents:
        raise ValueError("No code available for linting.")

    lint_errors = {}

    for filename, code in code_contents.items():

        result = run_linter_tool.invoke({
            "code_string": code
        })

        lint_errors[filename] = result

    history = state.get("history", [])

    history.append({
        "node": "lint_code_node",
        "status": "completed",
        "files_checked": list(code_contents.keys()),
    })

    return {
        "lint_errors": lint_errors,
        "history": history,
    }