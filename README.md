# Autonomous Code Review & Refactoring Agent with LangGraph

## Overview

An automated GitHub Pull Request code review system built using Python, LangGraph, and FastAPI.

The system fetches modified files from GitHub pull requests, analyzes Python code using linting and formatting tools, proposes code improvements, and pauses for human approval before applying changes.

## Features

- GitHub Pull Request integration.
- Automated Python code linting using Flake8 and Black.
- LangGraph-based workflow orchestration.
- Persistent workflow state using MemorySaver.
- Human-in-the-loop approval and rejection.
- Rejection feedback loop.
- GitHub API integration for committing approved changes.
- FastAPI endpoints and interactive Swagger documentation.
- Docker and Docker Compose support.
- Automated tests using pytest.

## Technology Stack

- Python 3.12
- LangGraph
- LangChain
- FastAPI
- GitHub REST API
- Flake8
- Black
- Pytest
- Docker
- Docker Compose
- Groq

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
Human Approval (HITL)
        |
        +------ Rejected
        |          |
        |          v
        |     Refactor Again
        |          |
        |          v
        |     Human Approval
        |
        +------ Approved
                   |
                   v
            Apply Changes Node
                   |
                   v
             GitHub Commit
```

## Project Structure

```text
code-review-agent/
│
├── app/
│   ├── api/
│   │   └── main.py
│   ├── graph/
│   │   ├── state.py
│   │   ├── nodes.py
│   │   ├── refactor.py
│   │   └── workflow.py
│   └── tools/
│       ├── github_client.py
│       └── sandbox_tool.py
│
├── tests/
│   ├── test_api.py
│   ├── test_linter.py
│   ├── test_refactor.py
│   └── test_rejection.py
│
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

Activate it on Windows:

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
REVIEW_API_KEY=your_review_api_key
```

Never commit your `.env` file or expose API keys.

### 5. Run the application

```bash
uvicorn app.api.main:app --reload
```

Application:

`http://127.0.0.1:8000`

Swagger documentation:

`http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application status |
| GET | `/health` | Health check |
| POST | `/api/webhooks/github` | Receive GitHub PR webhook |
| POST | `/api/reviews/{thread_id}/approve` | Approve or reject proposed changes |


### API Security

- GitHub webhook requests are verified using HMAC SHA-256.
- The webhook secret is configured using `GITHUB_WEBHOOK_SECRET`.
- The review approval endpoint requires an API key.
- Pass the API key using the `X-API-Key` request header.
- The API key is configured using `REVIEW_API_KEY`.
- Requests with invalid or missing credentials are rejected with HTTP 401.


### Approval Request Example

```json
{
  "approved": false,
  "feedback": "Please improve the code formatting."
}
```

To approve:

```json
{
  "approved": true,
  "feedback": null
}
```

## Run Tests

```bash
python -m pytest tests/ -v
```

## Run Using Docker

Build the Docker image:

```bash
docker build -t code-review-agent .
```

Run with Docker Compose:

```bash
docker compose up --build -d
```

Check running containers:

```bash
docker compose ps
```

Stop the application:

```bash
docker compose down
```

## Workflow State

The LangGraph workflow maintains the following state:

- `pr_url`
- `code_contents`
- `lint_errors`
- `refactored_code`
- `is_approved`
- `reviewer_feedback`
- `history`

The workflow uses MemorySaver for checkpoint persistence and interrupts before applying changes.


## Implementation Notes

- The refactoring node uses Groq-powered LLM integration to generate code improvements based on lint errors and reviewer feedback.
- The refactoring node uses the OpenAI-compatible LangChain interface configured with Groq.
- The generated code is validated through the review workflow and requires human approval before changes are applied.
- The linter runs Flake8 and Black in temporary directories using subprocess. This is not a fully isolated security sandbox.
- MemorySaver provides in-memory checkpointing; checkpoints do not survive application restarts.
- GitHub webhook signature verification is implemented using HMAC SHA-256.
- The approval endpoint uses API-key authentication through the X-API-Key header.
- Automated tests cover API security, linting errors, refactoring logic, and rejection handling.

## Future Improvements

- Implement stronger sandbox isolation for linting and code analysis.
- Introduce durable SQLite-based checkpoint persistence.
- Improve refactoring validation and automated code quality checks.
- Expand automated test coverage.

## Author

Developed as an assessment project demonstrating LangGraph workflow orchestration, GitHub integration, automated code analysis, and human-in-the-loop approval.
