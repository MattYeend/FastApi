# My API

User and product management API built with FastAPI, SQLAlchemy 2 and Alembic.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Set `DATABASE_URL` and generate an `API_KEY` in `.env`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Running

```bash
alembic upgrade head
fastapi dev app/main.py
```

Interactive docs are served at `/docs` only when `DEBUG=true`.

## Authentication

Every `/api/v1` endpoint requires the `X-API-Key` header. If `API_KEY` is not
configured the API refuses requests with a `503` rather than running open.

## Quality checks

```bash
ruff check .
ruff format --check .
pytest
pip-audit -r requirements.txt
```

## Structure

| Path                | Responsibility                               |
| ------------------- | -------------------------------------------- |
| `app/api/routes`    | HTTP layer, request and response handling    |
| `app/services`      | Business rules                               |
| `app/repositories`  | Database access                              |
| `app/schemas`       | Pydantic request and response models         |
| `app/models`        | SQLAlchemy models                            |
| `app/dependencies`  | Database session and authentication          |
| `app/middleware`    | Security headers                             |
| `app/core`          | Settings and domain exceptions               |