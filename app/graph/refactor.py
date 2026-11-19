
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.graph.state import ReviewState

load_dotenv()


def propose_refactor_node(state: ReviewState) -> dict:
    code_contents = state.get("code_contents", {})
    lint_errors = state.get("lint_errors", {})
    reviewer_feedback = state.get("reviewer_feedback")

    if not code_contents:
        raise ValueError("No code available for refactoring.")

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing.")

    model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    llm = ChatOpenAI(
        model=model_name,
        temperature=0,
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    refactored_code = {}

    for filename, original_code in code_contents.items():
        errors = lint_errors.get(filename, "No lint results available.")

        prompt = f"""You are an expert Python code refactoring assistant.

FILE NAME:
{filename}

ORIGINAL CODE:
{original_code}

LINT ERRORS:
{errors}

REVIEWER FEEDBACK:
{reviewer_feedback or "No additional reviewer feedback."}

REQUIREMENTS:
1. Fix reported linting and formatting errors.
2. Follow reviewer feedback.
3. Preserve original functionality and business logic.
4. Do not remove existing functionality.
5. Do not introduce unnecessary dependencies.
6. Return ONLY the complete corrected Python source code.
7. Do not include Markdown code fences or explanations.
"""

        response = llm.invoke(prompt)
        corrected_code = response.content

        if not isinstance(corrected_code, str):
            raise ValueError(
                f"LLM returned an invalid response for {filename}."
            )

        corrected_code = corrected_code.strip()

        if not corrected_code:
         raise ValueError(f"LLM returned empty code for {filename}.")

        corrected_code += "\n"

        refactored_code[filename] = corrected_code

    history = list(state.get("history", []))

    history.append(
        {
            "node": "propose_refactor_node",
            "status": "completed",
            "mode": "llm",
            "provider": "groq",
            "model": model_name,
            "reviewer_feedback": reviewer_feedback,
            "files_refactored": list(refactored_code.keys()),
        }
    )

    return {
        "refactored_code": refactored_code,
        "history": history,
        "is_approved": None,
    }
