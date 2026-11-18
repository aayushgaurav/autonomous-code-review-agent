
import subprocess
import sys
import tempfile
from pathlib import Path

from langchain_core.tools import tool


@tool
def run_linter_tool(code_string: str) -> str:
    """
    Analyze Python code using Flake8 and Black.

    Writes code to a temporary file, runs static
    analysis tools, and returns their outputs.
    """

    if not code_string.strip():
        return "ERROR: Empty Python code provided."

    with tempfile.TemporaryDirectory(
        prefix="code_review_"
    ) as temp_dir:

        file_path = Path(temp_dir) / "review_code.py"

        try:
            file_path.write_text(
                code_string,
                encoding="utf-8"
            )

            results = []

            # Run Flake8
            flake8_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "flake8",
                    str(file_path),
                ],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=temp_dir,
                shell=False,
            )

            results.append("=== FLAKE8 RESULTS ===")
            results.append(flake8_result.stdout)
            results.append(flake8_result.stderr)

            results.append(
                f"Flake8 exit code: {flake8_result.returncode}"
            )

            # Run Black in check-only mode
            black_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "black",
                    "--check",
                    str(file_path),
                ],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=temp_dir,
                shell=False,
            )

            results.append("\n=== BLACK RESULTS ===")
            results.append(black_result.stdout)
            results.append(black_result.stderr)

            results.append(
                f"Black exit code: {black_result.returncode}"
            )

            if (
                flake8_result.returncode == 0
                and black_result.returncode == 0
            ):
                results.append("\nSTATUS: PASSED")
            else:
                results.append("\nSTATUS: ISSUES FOUND")

            return "\n".join(
                item for item in results if item
            )

        except subprocess.TimeoutExpired:
            return "ERROR: Linter execution timed out."

        except OSError as error:
            return f"ERROR: Could not execute linter: {error}"
