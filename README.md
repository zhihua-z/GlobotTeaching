# Globot Teaching

AI-powered teaching platform with vector search capabilities.

## Tech Stack

| Layer    | Technology                                      |
| -------- | ----------------------------------------------- |
| Frontend | TypeScript, Next.js 14, TailwindCSS, shadcn/ui  |
| Backend  | Python FastAPI                                  |
| Database | PostgreSQL + pgvector                           |
| Infra    | Docker Compose                                   |

## Project Structure

```
.
├── docs/                    # Documentation (empty for now)
├── frontend/                # Next.js 14 application
│   ├── app/                 # App Router pages & layouts
│   ├── components/
│   │   └── ui/              # shadcn/ui components
│   ├── lib/                 # Shared utilities
│   ├── Dockerfile
│   └── package.json
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routers/         # API route handlers
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── config.py        # App settings
│   │   ├── database.py      # DB engine & session
│   │   └── main.py          # FastAPI entry point
│   ├── Dockerfile
│   └── requirements.txt
└── docker-compose.yml
```

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