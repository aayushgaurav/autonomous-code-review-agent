
import os
import base64
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_API = "https://api.github.com"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN is missing. Check your .env file.")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def github_request(endpoint: str, params=None):
    """Send an authenticated request to the GitHub REST API."""

    url = f"{GITHUB_API}{endpoint}"

    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=30,
    )

    response.raise_for_status()
    return response.json()


def get_pull_request(owner: str, repo: str, pr_number: int):
    """Retrieve Pull Request details from GitHub."""

    endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}"

    pr = github_request(endpoint)

    return {
        "pr_number": pr["number"],
        "title": pr["title"],
        "state": pr["state"],
        "base_branch": pr["base"]["ref"],
        "head_branch": pr["head"]["ref"],
        "head_sha": pr["head"]["sha"],
        "repository": pr["base"]["repo"]["full_name"],
        "head_repository": (
            pr["head"]["repo"]["full_name"]
            if pr["head"]["repo"]
            else None
        ),
        "pr_url": pr["html_url"],
    }


def get_modified_files(owner: str, repo: str, pr_number: int):
    """Retrieve files modified in a Pull Request."""

    endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/files"

    return github_request(endpoint)


def get_file_content(
    owner: str,
    repo: str,
    file_path: str,
    ref: str,
):
    """Retrieve actual source code from a GitHub file."""

    safe_path = quote(file_path, safe="/")

    endpoint = f"/repos/{owner}/{repo}/contents/{safe_path}"

    file_data = github_request(
        endpoint,
        params={"ref": ref},
    )

    if isinstance(file_data, list):
        raise ValueError(f"{file_path} is not a regular file.")

    if file_data.get("encoding") != "base64":
        raise ValueError(f"Unsupported file encoding: {file_path}")

    encoded_content = file_data.get("content", "")
    decoded_content = base64.b64decode(encoded_content)

    return decoded_content.decode("utf-8")


def fetch_pr_code(owner: str, repo: str, pr_number: int):
    """
    Fetch PR details, modified files and their source code.
    """

    pr_details = get_pull_request(owner, repo, pr_number)

    modified_files = get_modified_files(
        owner,
        repo,
        pr_number,
    )

    code_contents = {}

    for file in modified_files:

        # Skip deleted files
        if file["status"] == "removed":
            continue

        # Skip non-Python files for our initial implementation
        if not file["filename"].endswith(".py"):
            continue

        content = get_file_content(
            owner=owner,
            repo=repo,
            file_path=file["filename"],
            ref=pr_details["head_sha"],
        )

        code_contents[file["filename"]] = content

    return {
        "pr_details": pr_details,
        "modified_files": modified_files,
        "code_contents": code_contents,
    }


def apply_refactored_code(
    owner: str,
    repo: str,
    pr_number: int,
    refactored_code: dict,
):
    """
    Commit refactored files to the source branch of a GitHub PR.
    """

    if not refactored_code:
        raise ValueError("No refactored code provided.")

    pr_details = get_pull_request(owner, repo, pr_number)

    if pr_details["state"] != "open":
        raise ValueError("Cannot commit to a closed pull request.")

    head_repository = pr_details["head_repository"]

    if not head_repository:
        raise ValueError("The PR source repository is unavailable.")

    head_owner, head_repo = head_repository.split("/", 1)
    branch = pr_details["head_branch"]

    commit_results = []

    for file_path, code in refactored_code.items():

        safe_path = quote(file_path, safe="/")

        file_data = github_request(
            f"/repos/{head_owner}/{head_repo}/contents/{safe_path}",
            params={"ref": branch},
        )

        if isinstance(file_data, list):
            raise ValueError(f"Invalid file: {file_path}")

        encoded_content = base64.b64encode(
            code.encode("utf-8")
        ).decode("utf-8")

        response = requests.put(
            f"{GITHUB_API}/repos/{head_owner}/{head_repo}/contents/{safe_path}",
            headers=HEADERS,
            json={
                "message": f"Refactor {file_path}",
                "content": encoded_content,
                "sha": file_data["sha"],
                "branch": branch,
            },
            timeout=30,
        )

        response.raise_for_status()

        commit_data = response.json()

        commit_results.append({
            "file": file_path,
            "commit_sha": commit_data["commit"]["sha"],
            "commit_url": commit_data["commit"]["html_url"],
        })

    return commit_results