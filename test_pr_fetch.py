
import os
from dotenv import load_dotenv

from app.tools.github_client import fetch_pr_code

load_dotenv()

OWNER = os.getenv("GITHUB_OWNER")
REPO = os.getenv("GITHUB_REPO")

if not OWNER or not REPO:
    raise RuntimeError("Check GITHUB_OWNER and GITHUB_REPO in .env")

pr_number = int(input("Enter GitHub Pull Request number: "))

try:
    result = fetch_pr_code(
        owner=OWNER,
        repo=REPO,
        pr_number=pr_number,
    )

    print("\n========== PULL REQUEST DETAILS ==========")
    print(result["pr_details"])

    print("\n========== MODIFIED FILES ==========")

    for file in result["modified_files"]:
        print(file["filename"], "| Status:", file["status"])

    print("\n========== RETRIEVED PYTHON CODE ==========")

    for filename, code in result["code_contents"].items():
        print(f"\nFile: {filename}")
        print("-" * 50)
        print(code)

    print("\nSUCCESS: GitHub PR code retrieved!")

except Exception as error:
    print("\nFAILED:", error)
