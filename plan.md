# PenguWave — Plan

## Goal:
🎯 Project Objective: Track A - BackendThe main goal is to build a real backend for PenguWave that is both correct and secure, and connect the existing frontend to it.  To achieve a fully functional end-to-end system, the backend must fulfill the following core requirements:Implement the API Contract: Build and expose the server endpoints exactly as described in docs/api_contract.md (covering authentication, events, and users).  Handle Authentication & Sessions: Manage the complete user session lifecycle, including login, logout, and securely identifying who the current user is.  Enforce Authorization (RBAC): Handle role-based access control where different users have different roles. We must decide who is allowed to see and do what, and strictly enforce it at the server level.  Ensure Data Persistence: Store all events, users, and credentials in a database in a way that securely survives an application restart.  Input Validation & Error Handling: Validate all incoming data payloads and parameters strictly, and ensure the API returns sensible, consistent error messages. 


## Notes / Content (add your content here)
# Architecture Decision Records (ADR) - PenguWave Backend

This document logs the key architectural and design decisions made during the development of the PenguWave backend, including the rationale, tradeoffs, and security considerations for each decision.

---

## ADR 1: Backend Language and Framework

### Status
Accepted

### Context
The PenguWave starter app provides a frontend with an API contract (`docs/api_contract.md`). We need to build a secure, robust backend to replace the mock data and handle authentication, events, and user management.

### Decision
We will use **Python** with the **FastAPI** framework.

### Rationale
- **Speed of Development:** FastAPI allows for rapid development with minimal boilerplate code, which is crucial given the open-ended timeline of the project.
- **Automatic Documentation:** FastAPI automatically generates interactive API documentation (Swagger UI / ReDoc). This makes testing endpoints and aligning with the provided API contract seamless.
- **Built-in Validation:** Powered by Pydantic, FastAPI enforces strict input validation and sanitization out of the box, reducing the surface area for security vulnerabilities (injection, bad data formats) and ensuring consistent error delivery.

---

## ADR 2: Data Storage (Database)

### Status
Accepted

### Context
The application needs to store security events, user sessions, and credentials in a way that survives an application restart. The source data includes complex relational entities such as users, roles, and realistic mock security event logs (`data/mock_events.json`).

### Decision
We will use **PostgreSQL** as our primary relational database, **run locally** (native local install / local service — not a hosted/cloud DB). Connection details supplied via environment variables (never committed).

### Rationale
- **Scalability and Performance:** PostgreSQL is a production-grade, highly scalable relational database capable of handling large volumes of messy, real-world security logs efficiently.
- **Data Integrity:** Strict schema enforcement ensures that missing fields or malformed records (e.g., event severity levels) are caught at the database level.
- **Security Features:** PostgreSQL offers robust access control mechanisms, encryption capabilities, and reliable connection handling, ensuring user and system data remain secure.

---

## ADR 3: Authentication Mechanism

### Status
Accepted

### Context
We need a secure way to authenticate users and maintain sessions (Login, Logout, and Identity verification) while protecting against common web vulnerabilities like XSS and CSRF.

### Decision
We will use **OAuth2 with JWT (JSON Web Tokens)**, delivered and stored via **Secure, HttpOnly SameSite Cookies**.

### Rationale
- **XSS Protection:** Storing the JWT in an `HttpOnly` cookie ensures that client-side JavaScript cannot access the token, effectively neutralizing token-theft via Cross-Site Scripting (XSS) attacks.
- **FastAPI Ecosystem:** FastAPI provides excellent out-of-the-box support for OAuth2 password flows and dependency injection (`Depends`), making current-user verification clean and maintainable.
- **Scalability (Statelessness):** Since JWTs are cryptographically signed, the backend can verify the user's identity without querying the PostgreSQL database on every single API request, aligning with our scalability goals.
- **CSRF Mitigation:** To protect the cookies from Cross-Site Request Forgery (CSRF), we will strictly enforce `SameSite=Lax` or `SameSite=Strict` and require HTTPS (`Secure=True`) in production.

---

## ADR 4: Authorization Model (Access Control)

### Status
Accepted

### Context
The application requires role-based differentiation to control what data users can view and modify, enforcing strict security boundaries between operational tasks.

### Decision
We will implement **Role-Based Access Control (RBAC)** with **two roles — `admin` and `viewer`** — enforced via **FastAPI Dependencies**. This is strictly faithful to the API contract, which only distinguishes admin vs non-admin.

### Rationale & Role Definitions
- **`admin`**: Full system access. Uniquely authorized to manage system users (`/api/users` — list/create/update/delete) and assign roles. (Contract: user endpoints require admin; non-admin → 403.)
- **`viewer`**: Authenticated, **read-only** access to security events (`GET /api/events`, `GET /api/events/:id`). No access to user management.
- **FastAPI Integration:** Custom dependency functions (e.g., `deps.require_role(["admin"])`) secure routes individually with minimal duplication.

> **Decided:** Only two roles. The contract names only `admin`; everyone else is a read-only `viewer`. The starter seed data's `analyst` user (`UsersPage.tsx`) will be migrated to the `viewer` role (or dropped) when we seed the database.

---

## ADR 5: Project Folder Structure

### Status
Accepted

### Context
We need a clean, readable, and standard way to organize our backend files so that the code is maintainable and easy for team members to navigate.

### Decision
We will adopt a **Layered Architecture** pattern.

### Rationale
- **Separation of Concerns:** Keeping routes, database models, validation schemas, and business logic in separate directories prevents files from becoming bloated.
- **Readability:** This is a highly standard pattern in the FastAPI ecosystem. Anyone reviewing the project can immediately locate where endpoints are defined, how database tables are structured, and how data validation is handled.
- **Folder Blueprint:**
```text
  backend/
  └── app/
      ├── main.py          # Application entrypoint
      ├── core/            # Security, config, JWT helpers
      ├── routers/         # API Endpoints (auth.py, events.py, users.py)
      ├── models/          # SQLModel database tables
      ├── schemas/         # Pydantic validation schemas (if separate)
      └── crud/            # Database queries & operations

## ADR 6: Database Toolkit (ORM)

### Status
Accepted

### Context
To ensure that all system data (users, events, and sessions) survives an application restart, the Python server needs an Object-Relational Mapping (ORM) framework to communicate with the PostgreSQL database. 

### Decision
We will use **SQLModel** as our ORM and database toolkit.

### Rationale
- **Code Efficiency & No Duplication:** SQLModel combines the power of SQLAlchemy (for database interactions) and Pydantic (for data validation) into a single model definition. This eliminates the need to write separate, redundant classes for database tables and API schemas.
- **Type Safety & Developer Experience:** Built specifically for modern Python and FastAPI, SQLModel offers seamless autocomplete and type-checking in the IDE, drastically reducing runtime bugs and speeding up development.
- **Maintainability:** Maintaining a single source of truth for our data models makes schema changes much simpler and less prone to inconsistencies.

---

## ADR 7: Core Security Configurations (Password Hashing & CORS)

### Status
Accepted

### Context
Handling authentication and user accounts requires protecting sensitive user credentials. Additionally, because the React frontend runs on a different port than the FastAPI backend, we must explicitly allow cross-origin communication without exposing the server to unauthorized external entities.

### Decision
We will implement **Bcrypt** for password hashing and enforce a **strict CORS whitelist** restricting access solely to the local frontend origin (e.g., `http://localhost:5173`).

### Rationale
- **Industrial-Grade Hashing (Bcrypt):** User passwords will never be stored in plain text. Bcrypt uses a slow, computationally intensive hashing algorithm with built-in salting, making it highly resilient against brute-force and rainbow table attacks.
- **Strict CORS Control:** Instead of allowing wildcard access (`allow_origins=["*"]`), which would leave our secure API vulnerable, we will explicitly whitelist only our trusted frontend address. This prevents malicious third-party websites from making cross-origin requests to our endpoints.
- **Error Consistency:** Combined with FastAPI's native error response structures, this configuration helps ensure that unauthorized access attempts or validation failures return sensible, consistent error payloads.

## Tasks

### Task 1 (FIRST): Fix existing hardcoded values & bugs in the starter
Issues found during the security/quality scan. Per the decisions below, these are
split into fixes done **now** (pure frontend) and fixes **deferred** to when the
frontend is wired to the new backend (so auth/RBAC/passwords are done once, correctly).

**Decisions (locked):**
- Sequencing: **fix alongside backend wiring** — do pure-frontend fixes now; defer auth/RBAC/password fixes until backend exists.
- XSS: **render as plain text** — remove HTML rendering entirely (React auto-escaping); drop `sanitizeHtml`/`dangerouslySetInnerHTML`/`innerHTML`.
- Frontend auth: **cookie only** — remove the `X-Api-Key`; rely solely on the HttpOnly session cookie.
- Token storage: **HttpOnly cookie** — backend sets JWT in an HttpOnly cookie; frontend never touches the token in JS (requires CORS credentials + CSRF handling).

#### Task 1a — Do now (pure frontend cleanup)
- [ ] Remove the hardcoded API secret `pw_live_sk_...` from `src/api.ts:4`; remove all `X-Api-Key` headers. Treat the key as leaked/rotated.
- [ ] Fix XSS — replace `sanitizeHtml()` usage with plain-text rendering: event `description` (`EventsPage.tsx:138`) and search reflection (`EventsPage.tsx:55`); remove the no-op `sanitizeHtml` in `utils.ts`. (Live payload exists at `data/mock_events.json:247`.)
- [ ] Remove credential logging — `console.log` of email/password in `LoginModal.tsx:13` and `api.ts:7`.
- [ ] Add a `.gitignore` (node_modules, `.env*`, build output) — currently missing.
- [ ] Handle `CRITICAL` severity end-to-end — missing from `types.ts:5`, severity filter, and `severityColor` (`EventsPage.tsx:22`, renders CRITICAL as green).

#### Task 1b — Deferred to backend wiring (done once, correctly)
- [ ] Auth token → **HttpOnly cookie**; remove `localStorage` token (`api.ts:14`). Set up CORS credentials + CSRF.
- [ ] Stop storing/displaying plaintext passwords — remove hardcoded creds + "Password" column (`UsersPage.tsx`), remove `password` from client `User` type (`types.ts:19`); fetch users from backend.
- [ ] Enforce authorization on the **backend** (no client-trusted roles) — remove `isAdmin()` localStorage check (`utils.ts:25`), resolve `UsersPage.tsx:6-7` TODO via real role gating.
- [ ] Fix the login flow — handle success/failure with error feedback, align with cookie auth (`LoginModal.tsx:16-29`).
- [ ] Add input validation; remove/guard `DEBUG_BYPASS_AUTH` (`App.tsx:10`).

### Task 2: Project restructure — separate frontend / backend
(Scaffold backend package per ADR-5 layout; details TBD.)

## Open Questions (to be answered before implementation)
**Resolved:**
- Roles → use contract roles `admin` / `analyst` / `viewer` (ADR-4 updated).
- Database → PostgreSQL, run locally (ADR-2 updated).
- All Task 1 design questions resolved (see "Decisions (locked)" above).

- Roles → **two roles only: `admin` + `viewer`** (ADR-4 updated). Seed `analyst` user migrates to `viewer`.

**Still open:**
- _(none — all current design questions resolved)_

