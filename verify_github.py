
import os
from dotenv import load_dotenv

from app.tools.github_client import github_request

load_dotenv()

owner = os.getenv("GITHUB_OWNER")
repo = os.getenv("GITHUB_REPO")

try:
    user = github_request("/user")
    repository = github_request(f"/repos/{owner}/{repo}")

    print("\nGitHub Authentication Successful!")
    print("Authenticated user:", user["login"])
    print("Repository:", repository["full_name"])
    print("Repository access:", repository["permissions"])

except Exception as error:
    print("GitHub connection failed:", error)
