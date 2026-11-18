
import os
import hmac
import hashlib

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

load_dotenv()

def verify_github_signature(payload: bytes, signature: str) -> bool:
    """Verify that the webhook request came from GitHub."""

    secret = os.getenv("GITHUB_WEBHOOK_SECRET")

    if not secret or not signature:
        return False

    expected_signature = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)



app = FastAPI(
    title="Autonomous Code Review Agent",
    description="AI-powered GitHub Pull Request Review and Refactoring Agent",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Autonomous Code Review Agent API is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

class GitHubWebhookPayload(BaseModel):
    action: str
    pull_request: dict
    repository: dict



@app.post("/api/webhooks/github")
async def github_webhook(request: Request):

    # Step 1: Verify GitHub webhook signature
    signature = request.headers.get("X-Hub-Signature-256", "")
    body = await request.body()

    if not verify_github_signature(body, signature):
        raise HTTPException(
            status_code=401,
            detail="Invalid GitHub webhook signature.",
        )

    # Step 2: Validate webhook payload
    try:
        payload = GitHubWebhookPayload.model_validate_json(body)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook payload.",
        )

    # Step 3: Process only opened or synchronized PRs
    if payload.action not in ["opened", "synchronize"]:
        return {
            "message": "Event ignored",
            "action": payload.action,
        }

    pr_url = payload.pull_request.get("html_url")

    if not pr_url:
        raise HTTPException(
            status_code=400,
            detail="Pull request URL is missing.",
        )

    thread_id = (
        f"github-{payload.repository.get('full_name')}"
        f"-pr-{payload.pull_request.get('number')}"
    )

    initial_state = {
        "pr_url": pr_url,
        "code_contents": {},
        "lint_errors": {},
        "refactored_code": {},
        "is_approved": None,
        "reviewer_feedback": None,
        "history": [],
    }

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    from app.graph.workflow import graph

    graph.invoke(initial_state, config=config)

    return {
        "message": "Code review started.",
        "thread_id": thread_id,
        "pr_url": pr_url,
    }

class ReviewDecision(BaseModel):
    approved: bool
    feedback: Optional[str] = None


@app.post("/api/reviews/{thread_id}/approve")
def review_decision(
    thread_id: str,
    decision: ReviewDecision,
):
    from app.graph.workflow import graph

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    snapshot = graph.get_state(config)

    if not snapshot.values:
        raise HTTPException(
            status_code=404,
            detail="Review thread not found.",
        )

    if "apply_changes_node" not in snapshot.next:
        raise HTTPException(
            status_code=409,
            detail="Review is not waiting for a decision.",
        )

    graph.update_state(
        config,
        {
            "is_approved": decision.approved,
            "reviewer_feedback": (
                decision.feedback
                if not decision.approved
                else None
            ),
        },
    )

    graph.invoke(None, config=config)

    return {
        "message": (
            "Changes approved and applied."
            if decision.approved
            else "Changes rejected. Refactoring requested."
        ),
        "thread_id": thread_id,
        "approved": decision.approved,
    }