
from typing import TypedDict, Optional, List, Dict, Any


class ReviewState(TypedDict):
    """
    Stores the complete state of a code review session.
    """

    pr_url: str

    code_contents: Dict[str, str]

    lint_errors: Dict[str, str]

    refactored_code: Dict[str, str]

    is_approved: Optional[bool]

    reviewer_feedback: Optional[str]

    history: List[Dict[str, Any]]
