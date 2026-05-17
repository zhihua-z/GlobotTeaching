# Globot Teaching

AI-powered teaching platform with vector search capabilities. This monorepo contains a full-stack application for managing, searching, and analyzing educational questions (currently focused on 中国国家统一法律职业资格考试 / Chinese National Judicial Examination objective questions).

## Architecture Overview

```
                    ┌─────────────┐
                    │   Frontend  │  Next.js 14 (App Router)
                    │  :3000      │  TailwindCSS + shadcn/ui
                    └──────┬──────┘
                           │ HTTP (REST)
                    ┌──────▼──────┐
                    │   Backend   │  FastAPI (Python 3.12)
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
| Backend    | Python 3.12, FastAPI 0.115, SQLAlchemy 2.0 (async), Pydantic 2        |
| Database   | PostgreSQL 17 + pgvector 0.8 (vector similarity search)                |
| Auth       | JWT (python-jose) + bcrypt (passlib)                                   |
| Migration  | Alembic 1.14                                                           |
| Infra      | Docker Compose, multi-stage Docker builds                              |

## Project Structure

```
.
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── models/          # SQLAlchemy ORM models (Question, Document, Embeddings)
│   │   ├── routers/         # API route handlers (health, CRUD)
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── config.py        # Pydantic Settings (env-based config)
│   │   ├── database.py      # Async engine & session factory
│   │   └── main.py          # FastAPI app entry point
│   ├── alembic/             # Database migrations
│   ├── Dockerfile           # Multi-stage (not used, single-stage for dev)
│   ├── requirements.txt     # Python dependencies
│   └── .env.example
├── frontend/                # Next.js 14 frontend
│   ├── app/                 # App Router (layout.tsx, page.tsx, globals.css)
│   ├── components/ui/       # shadcn/ui components (Button)
│   ├── lib/                 # Shared utilities (cn() helper)
│   ├── src/types/           # TypeScript type definitions
│   ├── Dockerfile           # Multi-stage build (deps → builder → runner)
│   ├── next.config.mjs      # standalone output for Docker
│   ├── tailwind.config.ts   # Custom theme with shadcn/ui tokens
│   └── .env.example
├── docs/                    # Documentation + exam question data
│   ├── 2014年法考客观题真题.md
│   ├── 2020年法考客观题真题.md
│   ├── 2021年法考客观题真题.md
│   ├── 2022年法考客观题真题.md
│   └── 题目分析(deepseek)implementation_plan.md
├── docker-compose.yml       # Orchestrates db, backend, frontend
└── README.md
```

## Features (Planned / In Progress)

- **Question Bank**: Structured storage of questions with curriculum/subject/topic taxonomy
- **Vector Search**: PostgreSQL pgvector for semantic similarity search on questions (1024-dim embeddings)
- **Multiple Question Types**: single_choice, multiple_choice, true_false, fill_blank, short_answer, essay, code, matching, ordering
- **JWT Authentication**: Secure API access with token-based auth
- **Exam Paper Analysis**: Parse Chinese National Judicial Exam past papers from Markdown into structured data
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

| Method | Path          | Description       |
| ------ | ------------- | ----------------- |
| GET    | `/`           | Root              |
| GET    | `/api/health` | Health check      |
| GET    | `/docs`       | Swagger UI        |

## Sub-projects

For detailed documentation on each sub-project, see:

- [Backend README](./backend/README.md) — FastAPI server, models, API, migrations
- [Frontend README](./frontend/README.md) — Next.js app, components, types
- [Docs README](./docs/README.md) — Documentation and exam question data