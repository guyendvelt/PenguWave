# PenguWave Backend

FastAPI backend for the PenguWave security operations portal. See the root
[`plan.md`](../plan.md) for architecture decisions (ADRs).

> **Status:** scaffold. The app boots with a `/health` endpoint and a strict CORS
> whitelist. Auth, events, and users endpoints are added in later tasks.

## Stack

- Python + **FastAPI** (ADR-1)
- **PostgreSQL**, run locally (ADR-2) + **SQLModel** ORM (ADR-6)
- Dependency management: **pip + requirements.txt + venv**

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env   # then edit .env with your local values
```

> `.env` is gitignored — never commit it.

## Run

```bash
# from backend/, with the venv active
uvicorn app.main:app --reload --port 3001
```

The API listens on `http://localhost:3001` (the base URL in
[`docs/api_contract.md`](../docs/api_contract.md)). Check it:

```bash
curl http://localhost:3001/health   # -> {"status":"ok"}
```

## Test

```bash
pytest
```

## Layout

```
backend/
└── app/
    ├── main.py        # FastAPI app entrypoint
    ├── core/          # config, security, JWT helpers
    ├── routers/       # API endpoints (auth, events, users)
    ├── models/        # SQLModel database tables
    ├── schemas/       # Pydantic request/response schemas
    └── crud/          # database queries & operations
```
