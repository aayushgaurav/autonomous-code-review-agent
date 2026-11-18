from app.graph.workflow import graph
from unittest.mock import patch

config = {
    "configurable": {
        "thread_id": "hitl-test-002"
    }
}

initial_state = {
    "pr_url": "https://github.com/aayushgaurav/code-review-agent-demo/pull/1",
    "code_contents": {},
    "lint_errors": {},
    "refactored_code": {},
    "is_approved": None,
    "reviewer_feedback": None,
    "history": [],
}


print("========== STARTING HITL TEST ==========")

# Start workflow
graph.invoke(initial_state, config=config)

snapshot = graph.get_state(config)

print("\n========== FIRST PAUSE ==========")
print("Next node:", snapshot.next)

assert "apply_changes_node" in snapshot.next

print("SUCCESS: First approval pause confirmed!")


# Simulate reviewer rejection
print("\n========== REVIEWER REJECTION ==========")

graph.update_state(
    config,
    {
        "is_approved": False,
        "reviewer_feedback": "Please improve the variable naming.",
    },
)

# Resume workflow
graph.invoke(None, config=config)

snapshot = graph.get_state(config)

print("\n========== AFTER REJECTION ==========")
print("Next node:", snapshot.next)
print(
    "Reviewer feedback:",
    snapshot.values.get("reviewer_feedback")
)
print(
    "Approval status:",
    snapshot.values.get("is_approved")
)

assert "apply_changes_node" in snapshot.next
assert snapshot.values.get("is_approved") is None

print("\nSUCCESS: Rejection loop returned for another review!")

print("\n========== REVIEWER APPROVAL ==========")

# Simulate reviewer approval
graph.update_state(
    config,
    {
        "is_approved": True,
        "reviewer_feedback": None,
    },
)

mock_result = [
    {
        "file": "sample.py",
        "commit_sha": "mock_commit_456",
        "commit_url": "https://github.com/mock/commit/456",
    }
]

# Prevent an actual GitHub commit
with patch(
    "app.graph.nodes.apply_refactored_code",
    return_value=mock_result,
) as mock_commit:

    graph.invoke(None, config=config)

    mock_commit.assert_called_once()

snapshot = graph.get_state(config)

print("Commit function calls:", mock_commit.call_count)
print("Workflow next:", snapshot.next)
print("Approval status:", snapshot.values["is_approved"])

assert mock_commit.call_count == 1
assert snapshot.next == ()

print("\nSUCCESS: Approval and workflow completion verified!")