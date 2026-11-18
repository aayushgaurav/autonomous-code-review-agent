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
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
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

- The current refactoring node uses a temporary mock implementation. It is not yet a live LLM-powered refactoring implementation.
- The linter runs Flake8 and Black in temporary directories using subprocess. This is not a fully isolated security sandbox.
- MemorySaver provides in-memory checkpointing; checkpoints do not survive application restarts.
- GitHub webhook signature verification and authentication for the approval endpoint should be added before production deployment.

## Future Improvements

- Integrate live LLM-powered code refactoring.
- Implement stronger sandbox isolation.
- Add GitHub webhook signature verification.
- Add authentication and authorization for reviewer decisions.
- Introduce durable SQLite-based checkpoint persistence.

## Author

Developed as an assessment project demonstrating LangGraph workflow orchestration, GitHub integration, automated code analysis, and human-in-the-loop approval.
