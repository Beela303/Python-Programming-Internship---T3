# TaskFlow API

A typed REST API built with Python, FastAPI, and Pydantic. It demonstrates RESTful endpoint design, request and response validation, dependency injection, HTTP status codes, JSON communication, structured errors, automated tests, and automatic API documentation.

## Features

- Create, retrieve, update, and delete tasks.
- Validate requests with Pydantic.
- Use typed request and response schemas.
- Inject a task service into route handlers.
- Return consistent JSON errors for validation and application-level failures.
- Generate OpenAPI documentation.
- Test API behavior using Pytest and FastAPI's TestClient (powered by HTTPX).

## Requirements

- Python 3.11 or newer
- pip

## Installation

Create a virtual environment from the project root:

```bash
python -m venv .venv
```

Activate it:

**Windows Command Prompt**
```cmd
.venv\Scripts\activate.bat
```

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**Linux/macOS**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the application

```bash
python -m uvicorn app.main:app --reload
```

Local base URL: `http://127.0.0.1:8000`

## Automatic documentation

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## API endpoints

| Method | Endpoint | Description | Success |
|---|---|---|---|
| POST | `/api/v1/tasks` | Create a task | 201 |
| GET | `/api/v1/tasks` | List tasks | 200 |
| GET | `/api/v1/tasks/{task_id}` | Retrieve a task | 200 |
| PATCH | `/api/v1/tasks/{task_id}` | Update task fields | 200 |
| DELETE | `/api/v1/tasks/{task_id}` | Delete a task | 204 |
| GET | `/health` | Health check | 200 |

## Example request

```json
{
  "title": "Learn FastAPI",
  "description": "Build a typed REST API",
  "priority": "high"
}
```

`title` is required and must contain 3–100 characters. `description` is optional and has a maximum length of 500 characters. `priority` can be `low`, `medium`, or `high`.

## Error contract

Errors use a consistent JSON structure:

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with ID 99 was not found.",
    "details": null
  }
}
```

Validation errors use the `VALIDATION_ERROR` code and include validation details. Empty PATCH requests return `400`; invalid input returns `422`; missing tasks return `404`.

## Run tests

```bash
python -m pytest -v
```

## HTTP and HTTPS

The development server uses HTTP on localhost. In production, deploy behind a TLS-configured platform, reverse proxy, or load balancer and expose the API over HTTPS. HTTPS protects traffic in transit but does not replace authentication or authorization.

## Current limitations

- Tasks are held in memory and disappear when the process restarts.
- Different worker processes do not share the same task collection.
- Authentication, authorization, rate limiting, and database persistence are not implemented.
- Production HTTPS configuration is deployment-specific.

## Suggested next steps

1. Add pagination and filtering.
2. Add SQLite or PostgreSQL using SQLAlchemy.
3. Introduce repository and database-session patterns.
4. Add authentication and per-user task access.
5. Add structured logging and unexpected-error monitoring.
6. Add Ruff, Mypy, and CI checks.
