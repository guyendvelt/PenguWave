# PenguWave: Security Operations Portal

A security operations portal for monitoring security events across your infrastructure.

The project is split into two packages: a React frontend and a FastAPI backend
(Track A). Architecture decisions are recorded in [`plan.md`](./plan.md); the task
brief is in [`ASSIGNMENT.md`](./ASSIGNMENT.md).

## Layout

```
PenguWave/
├── frontend/   # React + Vite + TypeScript app
├── backend/    # FastAPI backend (Python) — see backend/README.md
└── docs/       # API contract
```

## Getting started

### Frontend

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
```

The frontend currently runs on mock data (`frontend/data/mock_events.json`). It
will be wired to the backend in a later step.

### Backend

See [`backend/README.md`](./backend/README.md) for full setup. In short:

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env          # never commit .env
uvicorn app.main:app --reload --port 3001   # http://localhost:3001
```

## What's included

- React + Vite + TypeScript frontend (3 pages)
- FastAPI backend scaffold (`/health`; domain endpoints in progress)
- Realistic mock security events (`frontend/data/mock_events.json`)
- API endpoint contract (`docs/api_contract.md`)
