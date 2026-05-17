# Backend — Globot Teaching API

FastAPI-based backend service for the Globot Teaching platform, featuring async PostgreSQL access with pgvector for vector similarity search.

## Tech Stack

| Category       | Technology                                                       |
| -------------- | ---------------------------------------------------------------- |
| Runtime        | Python 3.12                                                      |
| Web Framework  | FastAPI 0.115, Uvicorn 0.34 (async ASGI server)                  |
| ORM            | SQLAlchemy 2.0 (async/await with asyncpg)                        |
| Validation     | Pydantic 2, Pydantic Settings 2 (env-based config)               |
| Database       | PostgreSQL 17 + pgvector 0.8                                     |
| Migrations     | Alembic 1.14                                                     |
| Auth           | python-jose (JWT), passlib (bcrypt hashing), python-multipart     |
| HTTP Client    | httpx 0.28                                                       |
| CORS           | FastAPI CORSMiddleware (built-in)                                 |
| Infra          | Docker (single-stage), Docker Compose                             |

## Dependencies

All dependencies are listed in `requirements.txt`:

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
asyncpg==0.30.0
psycopg2-binary==2.9.10
alembic==1.14.1
pgvector==0.4.0
pydantic==2.10.4
pydantic-settings==2.7.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.18
httpx==0.28.1
```

## Architecture

```
app/
├── __init__.py
├── main.py              # FastAPI app entry point, lifespan, CORS, router registration
├── config.py            # Pydantic Settings (reads from .env / environment)
├── database.py          # AsyncEngine, async_session_factory, Base, get_db()
├── models/
│   ├── __init__.py
│   ├── base.py          # TimestampMixin (id, created_at, updated_at)
│   ├── question.py      # Question model (curriculum, subject, type, stem, options, etc.)
│   ├── question_embedding.py  # QuestionEmbedding model (VECTOR(1024))
│   ├── document.py      # Document model (title, content, source)
│   └── embedding.py     # DocumentEmbedding model (VECTOR(1536))
├── routers/
│   ├── __init__.py
│   └── health.py        # GET /api/health
├── schemas/
│   ├── __init__.py
│   └── question.py      # QuestionBase, QuestionCreate, QuestionUpdate, QuestionResponse
│                        # + Embedding schemas (QuestionEmbeddingBase, etc.)
alembic/
├── env.py               # Alembic environment config
├── script.py.mako       # Migration template
└── versions/
    └── 0001_create_questions_and_embeddings.py  # Initial schema
```

### Data Models

**Question** (table: `questions`)
- Curriculum categorization: `curriculum`, `subject`, `topic_path` (hierarchical array)
- Metadata: `difficulty` (1-5), `type` (enum: multiple_choice, single_choice, true_false, fill_blank, short_answer, essay, code, matching, ordering)
- Content: `stem` (question body), `options` (JSONB), `answer`, `rubric` (JSONB), `solution`
- Variants: `variants` (array of UUIDs for linked questions)
- Source: `source_origin`
- Timestamps: `created_at`, `updated_at`

**QuestionEmbedding** (table: `question_embeddings`)
- Links to `questions.id` via FK (CASCADE delete)
- `embedding`: pgvector VECTOR(1024) — 1024-dimensional vector
- `model_name`: identifier for the embedding model used

**Document** (table: `documents`)
- General-purpose document storage: `title`, `content`, `source`

**DocumentEmbedding** (table: `document_embeddings`)
- Links to `documents.id` via FK (CASCADE delete)
- `embedding`: pgvector VECTOR(1536) — 1536-dimensional vector (OpenAI text-embedding-3-small)

## Configuration

Environment variables (via `.env` file or system environment):

| Variable                   | Default                                                          | Description                |
| -------------------------- | ---------------------------------------------------------------- | -------------------------- |
| `APP_NAME`                 | `Globot Teaching API`                                            | FastAPI title              |
| `DEBUG`                    | `true`                                                           | SQLAlchemy echo on/off     |
| `DATABASE_URL`             | `postgresql+asyncpg://postgres:postgres@localhost:5432/...`      | Async DB connection        |
| `DATABASE_URL_SYNC`        | `postgresql://postgres:postgres@localhost:5432/...`              | Sync DB (for Alembic)      |
| `SECRET_KEY`               | `change-me-to-a-random-secret`                                   | JWT signing key            |
| `ALGORITHM`                | `HS256`                                                          | JWT algorithm              |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440`                                                        | Token expiry               |
| `CORS_ORIGINS`             | `["http://localhost:3000"]`                                      | Allowed CORS origins       |

## Current API Endpoints

| Method | Path          | Description        |
| ------ | ------------- | ------------------ |
| GET    | `/`           | Root / health check |
| GET    | `/api/health` | Health check       |
| GET    | `/docs`       | Swagger UI         |

Additional CRUD endpoints for questions are planned but not yet implemented.

## Development

### With Docker

```bash
# From the project root:
docker compose up backend
```

### Without Docker

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ensure PostgreSQL 17 + pgvector is running
# Edit .env to point to your local database
uvicorn app.main:app --reload --port 8000
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1