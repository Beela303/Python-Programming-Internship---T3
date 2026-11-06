# Reading Room API

A modular, token-authenticated REST API built with **FastAPI, Pydantic v2 and SQLAlchemy 2**. It provides CRUD operations for a user's personal book collection, filtering, pagination, relational persistence, automated tests, interactive API docs and a Postman collection.

## Features

- Account registration and JWT bearer-token login.
- Salted scrypt password hashing; plaintext passwords are never stored.
- SQLAlchemy 2 ORM models with a one-to-many User -> Book relationship.
- Pydantic request validation and response serialization.
- Create, read, update and delete book endpoints.
- Pagination (`page`, `page_size`) and filters (`genre`, `status`, `search`).
- Per-user data isolation: users can only access their own books.
- Environment-based configuration and SQLite/PostgreSQL support.
- Consistent HTTP error status codes and useful `detail` messages.
- Pytest integration tests, Postman collection, demo script and architecture note.
- Docker Compose setup for PostgreSQL + API.

## Project structure

```text
reading_room_api/
├── app/
│   ├── api/routes/       # Authentication and book endpoints
│   ├── core/             # Settings and security
│   ├── db/               # SQLAlchemy base and session
│   ├── models/           # User and Book ORM models
│   ├── schemas/          # Pydantic contracts
│   └── main.py
├── docs/ARCHITECTURE.md
├── migrations/           # Alembic environment + initial migration
├── postman/              # Importable Postman collection
├── scripts/demo.py
├── tests/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11+
- pip
- Optional: Docker Desktop for PostgreSQL deployment

## Run locally (SQLite)

```bash
# 1. Create and activate a virtual environment
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

# 2. Install dependencies
python -m pip install -r requirements-dev.txt

# 3. Create your local environment file
cp .env.example .env
```

On Windows, copy `.env.example` to `.env` manually or run `Copy-Item .env.example .env` in PowerShell. Change `SECRET_KEY` to a long random value before exposing the service.

Create the database schema for a fresh local SQLite database:

```bash
alembic upgrade head
```

Start the development server:

```bash
uvicorn app.main:app --reload
```

- Health check: `http://127.0.0.1:8000/health`
- Swagger UI: `http://127.0.0.1:8000/api/v1/docs`
- ReDoc: `http://127.0.0.1:8000/api/v1/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/api/v1/openapi.json`

## API reference

All API routes are prefixed with `/api/v1`.

| Method | Endpoint | Authentication | Purpose |
|---|---|---:|---|
| POST | `/auth/register` | No | Create an account |
| POST | `/auth/login` | No | Obtain JWT (OAuth2 form: username=email, password) |
| POST | `/books` | Yes | Create a book |
| GET | `/books` | Yes | List/filter/page through owned books |
| GET | `/books/{book_id}` | Yes | Retrieve one owned book |
| PATCH | `/books/{book_id}` | Yes | Partially update an owned book |
| DELETE | `/books/{book_id}` | Yes | Delete an owned book |

### Example workflow

Register:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"reader@example.com","password":"StrongPass123"}'
```

Login (OAuth2 form encoding):

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=reader@example.com&password=StrongPass123"
```

Copy `access_token` from the response, then create a book:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/books \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Things Fall Apart","author":"Chinua Achebe","genre":"Fiction","status":"reading","publication_year":1958}'
```

List with pagination and filters:

```bash
curl "http://127.0.0.1:8000/api/v1/books?page=1&page_size=10&genre=Fiction&status=reading&search=Chinua" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

A list response has this shape:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 10,
  "pages": 0
}
```

Import `postman/Reading-Room-API.postman_collection.json` into Postman for ready-made requests. The login request stores its access token in the collection variable automatically.

## Automated tests

Tests use an isolated in-memory SQLite database; they do not touch your local database.

```bash
pytest
```

The suite covers registration/login, duplicate accounts, invalid credentials, protected routes, CRUD, filtering/pagination and cross-account access isolation.

## Run the demo

```bash
python -m scripts.demo
```

The demo registers a sample account, logs in, creates a book, lists it and checks service health. Captured example output is included in `outputs/demo_output.txt`.

## PostgreSQL with Docker Compose

```bash
docker compose up --build
```

The API uses the PostgreSQL service configured in Compose. In a separate terminal, apply the migration:

```bash
docker compose exec api alembic upgrade head
```

Stop services:

```bash
docker compose down
```

Persisted database data remains in the named Docker volume. To remove it too, use `docker compose down -v`.

## Configuration

Copy `.env.example` to `.env`. Supported settings include:

| Variable | Purpose |
|---|---|
| `APP_NAME` | API title |
| `APP_VERSION` | API version |
| `API_V1_PREFIX` | Versioned route prefix |
| `DATABASE_URL` | SQLAlchemy database URL |
| `SECRET_KEY` | JWT signing secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime |
| `CORS_ORIGINS` | Allowed browser origins as JSON array |

Never commit `.env` or production secrets. The checked-in Compose credentials are for local development only.

## Error behaviour

- `400` / `409`: business conflict (duplicate account uses 409).
- `401`: missing, invalid or expired authentication.
- `404`: resource not found or not owned by the current user.
- `422`: invalid request body or query parameter (FastAPI/Pydantic validation).
- `204`: successful delete with no response body.

FastAPI's validation errors follow its standard structured `detail` response. Unexpected server errors should be logged and monitored in a deployed environment; do not expose stack traces to clients.

## Production hardening checklist

This is a production-style learning project, not a claim of production certification. Before public deployment:
- Set a strong secret via a secrets manager and enforce HTTPS.
- Add rate limiting and brute-force protection to authentication.
- Add refresh-token rotation/revocation or integrate a mature identity provider.
- Add structured logs, monitoring, tracing and database backups.
- Configure trusted CORS origins, TLS termination and secure deployment secrets.
- Add CI checks, dependency scanning, coverage thresholds and migration checks.
- Review password policy, account lifecycle, privacy and threat model.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for design rationale.
