from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.graph.state import ReviewState
from app.graph.nodes import (
    fetch_pr_node,
    lint_code_node,
    apply_changes_node,
    review_decision_router,
)
from app.graph.refactor import propose_refactor_node


builder = StateGraph(ReviewState)


# Register nodes
builder.add_node("fetch_pr_node", fetch_pr_node)
builder.add_node("lint_code_node", lint_code_node)
builder.add_node(
    "propose_refactor_node",
    propose_refactor_node,
)
builder.add_node(
    "apply_changes_node",
    apply_changes_node,
)


# Initial workflow
builder.add_edge(START, "fetch_pr_node")
builder.add_edge("fetch_pr_node", "lint_code_node")
builder.add_edge("lint_code_node", "propose_refactor_node")
builder.add_edge(
    "propose_refactor_node",
    "apply_changes_node",
)


# Route after the reviewer decision
builder.add_conditional_edges(
    "apply_changes_node",
    review_decision_router,
    {
        "refactor": "propose_refactor_node",
        "end": END,
    },
)


# Persistent memory
memory = MemorySaver()


# Human-in-the-loop interrupt
graph = builder.compile(
    checkpointer=memory,
    interrupt_before=["apply_changes_node"],
)