from app.graph.workflow import graph


config = {
    "configurable": {
        "thread_id": "checkpoint-test-001"
    }
}

# Save initial state to the checkpoint
initial_state = {
    "pr_url": "https://github.com/aayushgaurav/code-review-agent-demo/pull/1",
    "code_contents": {},
    "lint_errors": {},
    "refactored_code": {},
    "is_approved": None,
    "reviewer_feedback": None,
    "history": [],
}

graph.update_state(
    config,
    initial_state,
)

# Retrieve saved state
saved_state = graph.get_state(config)

print("========== CHECKPOINT TEST ==========")
print("Thread ID:", config["configurable"]["thread_id"])
print("Saved PR URL:", saved_state.values["pr_url"])
print("Approval Status:", saved_state.values["is_approved"])
print("History:", saved_state.values["history"])

assert saved_state.values["pr_url"] == initial_state["pr_url"]

print("\nSUCCESS: LangGraph checkpoint preserved state!")