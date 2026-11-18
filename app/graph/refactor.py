from app.graph.state import ReviewState


def propose_refactor_node(state: ReviewState) -> dict:
    """
    Generate refactored code using a temporary mock.
    """

    code_contents = state.get("code_contents", {})
    lint_errors = state.get("lint_errors", {})
    reviewer_feedback = state.get("reviewer_feedback")

    if not code_contents:
        raise ValueError("No code available for refactoring.")

    refactored_code = {}

    for filename, original_code in code_contents.items():

        errors = lint_errors.get(
            filename,
            "No lint results available."
        )

        if filename == "sample.py":
            corrected_code = (
                "def calculate_total(price, quantity):\n"
                "    total = price * quantity\n"
                "    return total\n"
            )
        else:
            corrected_code = original_code

        refactored_code[filename] = corrected_code

    history = list(state.get("history", []))

    history.append({
        "node": "propose_refactor_node",
        "status": "completed",
        "mode": "mock",
        "reviewer_feedback": reviewer_feedback,
        "files_refactored": list(refactored_code.keys()),
    })

    return {
        "refactored_code": refactored_code,
        "history": history,
        "is_approved": None,
    }