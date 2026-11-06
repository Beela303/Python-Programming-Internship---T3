# Architecture note

## Domain
Reading Room is a personal reading-library service. An authenticated account owns its books. Each book has a title, author, genre, reading status and optional publication year.

## Request flow
HTTP request -> FastAPI router -> dependency injection (database session + authenticated user) -> SQLAlchemy model/query -> relational database -> Pydantic response schema.

## Modules
- `app/api/routes`: HTTP endpoints and transport-level status codes.
- `app/api/deps.py`: OAuth2 bearer-token and current-user dependency.
- `app/schemas`: validated request and response contracts.
- `app/models`: SQLAlchemy ORM entities and relationships.
- `app/db`: declarative base and session lifecycle.
- `app/core`: environment configuration and security helpers.
- `tests`: isolated SQLite integration tests.

## Data ownership and access
Every book query is scoped to the authenticated user's ID. A book owned by another account is deliberately returned as 404, avoiding disclosure that the resource exists.

## Persistence and migrations
SQLite is the zero-setup local default. Set `DATABASE_URL` to a PostgreSQL URL for deployment. Alembic is included for schema migration management; generate a migration after model changes with `alembic revision --autogenerate -m "describe change"` and apply it with `alembic upgrade head`.

## Authentication
Registration stores a salted scrypt password hash, never a plaintext password. Login issues a signed JWT bearer token with an expiration. This is a teaching implementation of core authentication concepts; production deployments should use a managed secret, HTTPS, rate limiting, refresh-token rotation/revocation strategy, audit logging and a reviewed identity/security design.

## Operational considerations
- Configure secrets and database URLs through environment variables.
- Use `pool_pre_ping` for stale database connections.
- Keep page sizes bounded (maximum 100).
- Add structured logging, metrics, tracing, backups and CI/CD before production launch.
