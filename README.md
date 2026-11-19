# Autonomous Code Review & Refactoring Agent with LangGraph

## Overview

An AI-powered GitHub Pull Request review and refactoring system built using Python, LangGraph, and FastAPI.

The agent fetches modified files from GitHub Pull Requests, analyzes Python code using automated linting and formatting tools, proposes AI-generated refactoring improvements, validates the proposed changes, and pauses for human approval before committing changes back to the PR branch.

## Features

- GitHub Pull Request integration through webhooks.
- Automated Python code linting using Flake8 and Black.
- AI-powered code refactoring using Groq.
- LangGraph-based workflow orchestration.
- Workflow checkpointing using MemorySaver.
- Automated validation of generated refactored code.
- Human-in-the-loop approval and rejection.
- Rejection feedback loop for iterative refactoring.
- GitHub REST API integration for committing approved changes.
- Webhook signature verification using HMAC SHA-256.
- API-key authentication for approval endpoints.
- FastAPI endpoints with interactive Swagger documentation.
- Docker and Docker Compose support.
- Automated testing using pytest.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Core application |
| LangGraph | Workflow orchestration and checkpointing |
| LangChain | LLM integration and tool interface |
| Groq | AI-powered code refactoring |
| FastAPI | API and webhook server |
| GitHub REST API | PR fetching and commit write-back |
| Flake8 | Python linting |
| Black | Code formatting validation |
| Pytest | Automated testing |
| Docker | Application containerization |
| Docker Compose | Container orchestration |

## Project Architecture

```text
GitHub Pull Request
        |
        v
GitHub Webhook (FastAPI)
        |
        v
Fetch PR Node
        |
        v
Lint Code Node
        |
        v
Propose Refactor Node
        |
        v
Validate Refactor Node
        |
        +------ Validation Failed
        |              |
        |              v
        |      Propose Refactor Again
        |
        +------ Validation Passed
                       |
                       v
              HITL Approval Pause
                       |
              +--------+--------+
              |                 |
              v                 v
           Rejected          Approved
              |                 |
              v                 v
      Refactor Again      Apply Changes Node
                                |
                                v
                         GitHub API Commit
                                |
                                v
                               END
```

## Project Structure

```text
code-review-agent/
│
├── app/
│   ├── api/
│   │   └── main.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   ├── nodes.py
│   │   ├── refactor.py
│   │   └── workflow.py
│   │
│   └── tools/
│       ├── github_client.py
│       └── sandbox_tool.py
│
├── tests/
│   ├── test_api.py
│   ├── test_linter.py
│   ├── test_refactor.py
│   ├── test_rejection.py
│   ├── test_refactor_retry.py
│   └── test_validation_node.py
│
├── test_live_webhook.py
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd code-review-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root.

```env
GITHUB_TOKEN=your_github_token_here
GITHUB_OWNER=your_github_username

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b

GITHUB_WEBHOOK_SECRET=your_webhook_secret
REVIEW_API_KEY=your_review_api_key_here
```

Never commit your `.env` file or expose API keys.

### 5. Run the application

```bash
uvicorn app.api.main:app --reload
```

Application:

http://127.0.0.1:8000

Swagger documentation:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application status |
| GET | `/health` | Health check |
| POST | `/api/webhooks/github` | Receive and process GitHub PR webhook |
| POST | `/api/reviews/{thread_id}/approve` | Approve or reject proposed changes |

## API Security

- GitHub webhook requests are verified using HMAC SHA-256.
- The webhook secret is configured using `GITHUB_WEBHOOK_SECRET`.
- The review approval endpoint requires API-key authentication.
- The API key is passed through the `X-API-Key` request header.
- The API key is configured using `REVIEW_API_KEY`.
- Requests with invalid or missing credentials are rejected with HTTP 401.

## Approval Request Examples

### Reject proposed changes

```json
{
  "approved": false,
  "feedback": "Please improve the code formatting."
}
```

### Approve proposed changes

```json
{
  "approved": true,
  "feedback": null
}
```

Approved changes are applied to the pull request branch through the GitHub REST API.

## Workflow State

The LangGraph workflow maintains the following state:

- `pr_url`
- `code_contents`
- `lint_errors`
- `refactored_code`
- `is_approved`
- `reviewer_feedback`
- `history`
- `validation_passed`

The workflow uses a checkpointer to maintain state during the review process and interrupts before applying changes, allowing a human reviewer to make the final decision.

## Workflow Execution

1. **Fetch PR Node:** Retrieves pull request details and modified files from GitHub.
2. **Lint Code Node:** Analyzes Python files using Flake8 and Black.
3. **Propose Refactor Node:** Uses an LLM to generate improved code based on linting results and reviewer feedback.
4. **Validate Refactor Node:** Validates the generated code using automated linting and formatting checks.
5. **Human-in-the-Loop:** Pauses execution until the reviewer approves or rejects the proposed changes.
6. **Apply Changes Node:** Writes approved changes to the GitHub PR branch and creates a commit.

If validation fails or the reviewer rejects the proposed changes, the workflow returns to the refactoring stage.

## Run Tests

Run the test suite:

```bash
python -m pytest tests/ -v
```

The test suite covers API security, linting, refactoring, validation, retry behavior, and rejection handling.

## Run Using Docker

Build the Docker image:

```bash
docker build -t code-review-agent .
```

Run using Docker Compose:

```bash
docker compose up --build -d
```

Check running containers:

```bash
docker compose ps
```

Check application logs:

```bash
docker logs code-review-container
```

Stop the application:

```bash
docker compose down
```

## Implementation Notes

- The refactoring node uses Groq through the OpenAI-compatible LangChain interface.
- Generated refactored code is validated before reaching the human approval stage.
- Human approval is required before applying changes to the GitHub repository.
- GitHub write-back is implemented using the GitHub Contents API.
- Live GitHub write-back was verified on a test Pull Request after human approval.
- The linter runs Flake8 and Black in temporary directories using subprocess. This is not a fully isolated security sandbox.
- MemorySaver provides in-memory checkpointing. Checkpoints do not survive application restarts.
- GitHub webhook signature verification is implemented using HMAC SHA-256.
- The approval endpoint uses API-key authentication through the `X-API-Key` header.

## Future Improvements

- Implement stronger sandbox isolation for linting and code execution.
- Introduce durable checkpoint persistence using SQLite or PostgreSQL.
- Improve automated code quality validation.
- Expand test coverage.
- Introduce more advanced reviewer feedback and code analysis capabilities.

## Author

Developed as an assessment project demonstrating AI-powered code review, LangGraph workflow orchestration, GitHub integration, automated validation, and human-in-the-loop approval.
