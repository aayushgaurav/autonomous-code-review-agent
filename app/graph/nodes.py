import re
from app.tools.sandbox_tool import run_linter_tool
from app.graph.state import ReviewState
from app.tools.github_client import fetch_pr_code
from app.tools.github_client import apply_refactored_code


def fetch_pr_node(state: ReviewState) -> dict:
    """
    Fetch modified Python files from a GitHub pull request.
    """

    pr_url = state["pr_url"].strip()

    pattern = (
        r"https://github\.com/"
        r"([^/]+)/([^/]+)/pull/(\d+)/?"
    )

    match = re.fullmatch(pattern, pr_url)

    if not match:
        raise ValueError("Invalid GitHub Pull Request URL.")

    owner, repo, pr_number = match.groups()

    pr_data = fetch_pr_code(
        owner=owner,
        repo=repo,
        pr_number=int(pr_number),
    )

    code_contents = pr_data["code_contents"]

    if not code_contents:
        raise ValueError(
            "No modified Python files found in this pull request."
        )

    history = state.get("history", [])

    history.append({
        "node": "fetch_pr_node",
        "status": "success",
        "pr_number": int(pr_number),
        "files_fetched": list(code_contents.keys()),
    })

    return {
        "code_contents": code_contents,
        "history": history,
    }


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

def apply_changes_node(state: ReviewState) -> dict:
    """
    Apply refactored code only after approval.
    """

    if state.get("is_approved") is False:
        history = list(state.get("history", []))

        history.append({
            "node": "apply_changes_node",
            "status": "rejected",
            "message": "Reviewer requested changes.",
        })

        return {"history": history}

    if state.get("is_approved") is not True:
        raise PermissionError(
            "Changes cannot be applied without approval."
        )

    pr_url = state["pr_url"].strip()

    pattern = (
        r"https://github\.com/"
        r"([^/]+)/([^/]+)/pull/(\d+)/?"
    )

    match = re.fullmatch(pattern, pr_url)

    if not match:
        raise ValueError("Invalid GitHub Pull Request URL.")

    owner, repo, pr_number = match.groups()

    refactored_code = state.get("refactored_code", {})

    if not refactored_code:
        raise ValueError("No refactored code available.")

    commit_results = apply_refactored_code(
        owner=owner,
        repo=repo,
        pr_number=int(pr_number),
        refactored_code=refactored_code,
    )

    history = list(state.get("history", []))

    history.append({
        "node": "apply_changes_node",
        "status": "completed",
        "commits": commit_results,
    })

    return {"history": history}

def review_decision_router(state: ReviewState) -> str:
    """
    Route rejected reviews back for refactoring.
    """

    if state.get("is_approved") is False:
        return "refactor"

    return "end"


def validate_refactor_node(state: ReviewState) -> dict:
    """
    Validate LLM-generated code using Flake8 and Black.
    """

    refactored_code = state.get("refactored_code", {})

    if not refactored_code:
        raise ValueError("No refactored code available for validation.")

    validation_errors = {}
    validation_passed = True

    for filename, code in refactored_code.items():
        result = run_linter_tool.invoke({
            "code_string": code
        })

        validation_errors[filename] = result

        if "STATUS: PASSED" not in result:
            validation_passed = False

    history = list(state.get("history", []))

    history.append({
        "node": "validate_refactor_node",
        "status": "passed" if validation_passed else "failed",
        "files_checked": list(refactored_code.keys()),
    })

    return {
        "lint_errors": validation_errors,
        "validation_passed": validation_passed,
        "history": history,
    }

def validation_decision_router(state: ReviewState) -> str:
    """
    Route based on refactored code validation results.
    """

    if state.get("validation_passed") is True:
        return "review"

    return "refactor"