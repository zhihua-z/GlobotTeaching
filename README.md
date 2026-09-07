# Globot Teaching

AI-powered teaching platform with vector search capabilities. This monorepo contains a full-stack application for managing, searching, and analyzing educational questions (currently focused on 中国国家统一法律职业资格考试 / Chinese National Judicial Examination objective questions).

## Architecture Overview

```
                    ┌─────────────┐
                    │   Frontend  │  Next.js 14 (App Router)
                    │  :3000      │  TailwindCSS + shadcn/ui
                    └──────┬──────┘
                           │ HTTP (REST) · httpOnly cookie JWT
                    ┌──────▼──────┐
                    │   Backend   │  FastAPI (Python 3.9+)
                    │  :8000      │  SQLAlchemy async + pgvector
                    └──────┬──────┘
                           │ SQL
                    ┌──────▼──────┐
                    │  Database   │  PostgreSQL 17 + pgvector
                    │  :5432      │  Vector embeddings (1024d)
                    └─────────────┘
```

## Tech Stack

| Layer      | Technology                                                             |
| ---------- | ---------------------------------------------------------------------- |
| Frontend   | TypeScript, Next.js 14.2 (App Router), React 18, TailwindCSS 3.4, shadcn/ui |
| Backend    | Python 3.9+, FastAPI 0.115, SQLAlchemy 2.0 (async), Pydantic 2        |
| Database   | PostgreSQL 17 + pgvector 0.8 (vector similarity search)                |
| Auth       | JWT (python-jose) + bcrypt (passlib) · httpOnly cookies · rate limiting |
| Migration  | Alembic 1.14                                                           |
| Infra      | Docker Compose, multi-stage Docker builds                              |

## Project Structure

```
.
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── models/          # SQLAlchemy ORM models (Question, Taxonomy, Auth, Embeddings)
│   │   ├── repositories/    # Data access layer (all SQL, no business logic)
│   │   ├── routers/         # API route handlers (health, questions, taxonomy, auth, analysis)
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── security/        # JWT, passwords, rate limiting
│   │   ├── services/        # Business logic + transaction boundaries
│   │   ├── config.py        # Pydantic Settings (env-based config)
│   │   ├── database.py      # Lazy async engine & session factory
│   │   ├── deps.py          # Dependency injection (get_current_user, require_admin)
│   │   ├── envelope.py      # Unified {data, error} response envelope
│   │   └── main.py          # FastAPI app entry point + lifespan
│   ├── alembic/             # Database migrations (0001–0003)
│   ├── scripts/ingest/      # Question bank ingestion pipeline
│   ├── tests/               # Pytest test suite (pytest-asyncio + httpx)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/                # Next.js 14 frontend (33 routes)
│   ├── app/                 # App Router with (auth), (student), admin route groups
│   │   ├── (auth)/login/    # Login page
│   │   ├── (student)/       # practice, review, mistakes, profile, chat, dashboard, progress, legal-articles, home
│   │   └── admin/           # questions, taxonomy, legal-articles, pipeline, review, prompts, evals
│   ├── components/          # UI components (shadcn/ui) + question/admin feature blocks
│   ├── lib/                 # API client, mocks, hooks, types, providers
│   ├── Dockerfile
│   └── ...
├── docs/                    # Documentation + implementation plans + exam question data
│   ├── implementation-plan/ # Detailed implementation plans (3 documents)
│   └── ...
├── docker-compose.yml       # Orchestrates db, backend, frontend
└── README.md
```

## Features

- **JWT Authentication**: httpOnly cookie-based auth with bcrypt passwords, token revocation, rate limiting, and audit logging
- **Unified API Envelope**: All responses use `{ data, error }` format with standardized error codes
- **Question Bank**: CRUD with structured storage, taxonomy (curricula/subjects/topics/question-types), and vector embeddings
- **Vector Search**: PostgreSQL pgvector for semantic similarity search on questions (1024-dim embeddings)
- **Multiple Question Types**: single_choice, multiple_choice, true_false, fill_blank, short_answer, essay, code, matching, ordering
- **Exam Paper Ingestion**: Parse Chinese National Judicial Exam past papers (2014/2020/2021/2022) from Markdown into structured data
- **AI-powered Features** (roadmap): Auto-solution generation, difficulty prediction, personalized recommendations

## Quick Start

### 1. Clone and enter the project

```bash
git clone <repo-url> globot-teaching
cd globot-teaching
```

### 2. Start all services with Docker Compose

```bash
docker compose up --build
```

This will start:

| Service  | URL                          |
| -------- | ---------------------------- |
| Frontend | http://localhost:3000         |
| Backend  | http://localhost:8000         |
| API Docs | http://localhost:8000/docs    |
| Database | localhost:5432                |

### 3. (Optional) Run locally without Docker

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Make sure PostgreSQL + pgvector is running
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev          # → http://localhost:3000
```

### 4. Environment Variables

Copy the example env files and adjust as needed:

```bash
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env
```

## API Endpoints

All endpoints are prefixed with `/api/v1` and use a unified `{ data, error }` envelope.

### Auth (`/auth`)

| Method | Path              | Description                     | Auth |
| ------ | ----------------- | ------------------------------- | ---- |
| POST   | `/auth/login`     | Login (sets httpOnly JWT cookie)| No   |
| POST   | `/auth/logout`    | Logout (revokes token)          | Yes  |
| GET    | `/auth/me`        | Current user info               | Yes  |

### Questions (`/questions`)

| Method | Path                            | Description                  |
| ------ | ------------------------------- | ---------------------------- |
| GET    | `/questions`                    | List/Filter/Search questions |
| POST   | `/questions`                    | Create question (admin)      |
| GET    | `/questions/{id}`              | Get question by ID           |
| PATCH  | `/questions/{id}`              | Update question (admin)      |
| DELETE | `/questions/{id}`              | Soft-delete question (admin) |
| GET    | `/questions/{id}/similar?k=10` | Vector similarity search     |
| GET    | `/questions/{id}/analysis`     | Full analysis + AI breakdown |
| POST   | `/questions/{id}/analysis/refresh` | Refresh AI breakdown     |
| POST   | `/questions/import`            | Bulk import (multipart/SSE)  |

### Taxonomy (`/curricula`, `/subjects`, `/topics`, `/question-types`)

| Method | Path                 | Description              |
| ------ | -------------------- | ------------------------ |
| GET    | `/curricula`         | List curricula           |
| POST   | `/curricula`         | Create curriculum (admin)|
| GET    | `/curricula/{id}`    | Get curriculum           |
| PATCH  | `/curricula/{id}`    | Update curriculum (admin)|
| DELETE | `/curricula/{id}`    | Delete curriculum (admin)|
| GET    | `/curricula/{id}/subjects` | List subjects      |
| POST   | `/subjects`          | Create subject (admin)   |
| GET    | `/subjects/{id}`     | Get subject              |
| PATCH  | `/subjects/{id}`     | Update subject (admin)   |
| DELETE | `/subjects/{id}`     | Delete subject (admin)   |
| GET    | `/subjects/{id}/topics`   | List topics          |
| POST   | `/topics`            | Create topic (admin)     |
| GET    | `/topics/{id}`       | Get topic                |
| PATCH  | `/topics/{id}`       | Update topic (admin)     |
| DELETE | `/topics/{id}`       | Delete topic (admin)     |
| GET    | `/question-types`    | List question types      |
| PATCH  | `/question-types/{code}` | Update type label (admin)|

### System (`/health`)

| Method | Path          | Description  |
| ------ | ------------- | ------------ |
| GET    | `/health`     | Health check |

## Implementation Progress

Implementation is tracked against [8 backend milestones](./docs/implementation-plan/IMPLEMENTATION-PLAN-3-BACKEND—后端API总实现计划.md):

| Milestone | Status      | Description                                  |
|-----------|-------------|----------------------------------------------|
| B1        | ✅ Done     | Layered skeleton + envelope + exception handling + config |
| B2        | ✅ Done     | Question bank + taxonomy + legal articles + search |
| B3        | ✅ Done     | Auth (JWT/cookie/RBAC/rate limiting/audit) + user seed |
| B4        | ✅ Done     | Prompt gateway + prompt templates + version management |
| B5        | ✅ Done     | Pipeline + review queue + evals (full stack)  |
| B6        | 📋 Planned  | FSRS + Profile (knowledge graph L1–L4)       |
| B7        | 📋 Planned  | Practice + Chat + Progress + Mistakes + Settings |
| B8        | 📋 Planned  | Dashboard + Reports + push notifications     |

**Last verified:** 2026-06-01 (17:05 SGT)

- **Test database:** `globot_test` created and all migrations applied successfully
- **Tests:** 145 tests collected, 145 passed, 4 skipped, 0 failures
- **Migrations:** 0001–0006 all apply cleanly on fresh databases
- **B4 – Prompt Templates:** Full stack (migration 0004, model, schemas, repo, service, router, 20 tests) — all passing
- **B5 – Pipeline + Review + Evals:** Full stack (migration 0005–0006, 2 models, 3 schemas, 3 repos, 3 services, 3 routers, 16 tests) — all passing
  - `POST /pipeline/upload` → creates `pipeline_runs(status=pending)`
  - `GET/POST /admin/review/queue` → CRUD `question_drafts` with approve/reject/bulk
  - `GET/POST /admin/evals/sets|runs|cases` → eval sets, cases, and runs
  - All admin endpoints guarded by `require_admin`, audit-logged
- **Migration idempotency:** `0003_add_indexes.py` updated to use `CREATE INDEX IF NOT EXISTS` with direct SQL for `DROP INDEX IF EXISTS` downgrade compatibility

## Sub-projects

For detailed documentation on each sub-project, see:

- [Backend README](./backend/README.md) — FastAPI server, models, API, migrations, security
- [Frontend README](./frontend/README.md) — Next.js app (33 routes with mock data), components, types
- [Docs README](./docs/README.md) — Documentation and exam question data
