# PenguWave: Security Operations Portal

A security operations portal for monitoring security events across your
infrastructure. The project is split into a **React frontend** and a **FastAPI
backend** (Track A: a real, secure backend with the existing frontend wired to it).

## Layout

```
PenguWave/
├── frontend/   # React + Vite + TypeScript app
└── backend/    # FastAPI backend (Python) — see backend/README.md
```

## Getting started

### Quick start: `./run.sh` (recommended)

`run.sh` launches the whole stack — backend (:3001) and frontend (:5173) — with one
command. It creates the Python venv and installs backend deps on first run, installs
frontend deps if needed, seeds the database, and starts both servers. Press
**Ctrl-C** to stop both.

**Prerequisites** (one-time):

```bash
# 1. A local PostgreSQL must be running, then create the database:
createdb penguwave

# 2. Configure the backend environment (never commit .env):
cp backend/.env.example backend/.env
#    Edit backend/.env and set at least:
#      SECRET_KEY        (python -c "import secrets; print(secrets.token_urlsafe(48))")
#      DATABASE_URL      (e.g. postgresql://<you>@localhost:5432/penguwave)
#      SEED_ADMIN_EMAIL / SEED_ADMIN_PASSWORD   (your initial admin login)
```

Then, from the repo root:

```bash
./run.sh              # start backend + frontend (seeds the DB first)
./run.sh --no-seed    # start without re-seeding the database
```

Open **http://localhost:5173**, click **Login**, and sign in with the
`SEED_ADMIN_*` credentials from `backend/.env`. Events and users load live from the
backend. (`http://localhost:3001` is the API only — it has no homepage; see `/docs`.)

> If a port is already in use, `run.sh` stops with a clear message. Free it with
> `lsof -ti tcp:3001 tcp:5173 | xargs kill` and retry.

### Manual start (alternative)

Run the backend first, then the frontend, in separate terminals:

```bash
# Backend  → http://localhost:3001
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env            # configure as above
createdb penguwave
python -m app.seed
uvicorn app.main:app --reload --port 3001

# Frontend → http://localhost:5173
cd frontend
npm install
npm run dev
```

See [`backend/README.md`](./backend/README.md) for details (generating a
`SECRET_KEY`, running tests, the full endpoint list).

## What was built

- **Authentication & sessions** — login / logout / current-user, with the JWT
  delivered in an **HttpOnly cookie** (never exposed to JavaScript). Passwords are
  hashed with **bcrypt**.
- **Authorization (RBAC)** — two roles: `admin` (manages users) and `viewer`
  (read-only on events). User endpoints are admin-only and return `403` otherwise.
- **Events & users APIs** — backed by **PostgreSQL** via SQLModel, with strict
  input validation and a consistent `{ "error": "..." }` response shape.
- **Frontend integration** — the React app talks to the backend over cookie-based
  sessions (`credentials: "include"`); no token is stored in the browser.
- **Security fixes to the starter** — removed a hardcoded API secret, fixed a
  stored/reflected **XSS** (event descriptions and search render as plain text),
  stopped logging credentials, and removed the plaintext-password UI.

## Key decisions

- **Cookie-only auth.** The JWT lives in an HttpOnly, SameSite cookie — login
  returns `{ user }` with no token in the body. A deliberate deviation from the
  contract's example, chosen for XSS safety.
- **Two roles only.** The contract distinguishes admin vs. non-admin; everyone who
  isn't an admin is a read-only `viewer`.
- **Messy data is preserved.** Non-core event fields are nullable, so incomplete
  real-world records (e.g. a missing `sourceIp`) are kept rather than dropped.

## Testing

```bash
cd backend && pytest        # backend unit + integration tests
cd frontend && npm test     # frontend unit tests (Jest + RTL)
```
