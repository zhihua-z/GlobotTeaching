# Backend — Globot Teaching API

FastAPI-based backend service for the Globot Teaching platform, featuring async PostgreSQL access with pgvector for vector similarity search, JWT authentication, and a layered architecture (routers → services → repositories).

## Tech Stack

| Category       | Technology                                                       |
| -------------- | ---------------------------------------------------------------- |
| Runtime        | Python 3.9+                                                      |
| Web Framework  | FastAPI 0.115, Uvicorn 0.34 (async ASGI server)                  |
| ORM            | SQLAlchemy 2.0 (async/await with asyncpg)                        |
| Validation     | Pydantic 2, Pydantic Settings 2 (env-based config)               |
| Database       | PostgreSQL 17 + pgvector 0.8                                     |
| Migrations     | Alembic 1.14                                                     |
| Auth           | python-jose (JWT) + passlib (bcrypt) + httpOnly cookies + rate limiting |
| Tests          | pytest + pytest-asyncio + httpx                                  |
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
pytest==8.4.2
pytest-asyncio==1.2.0
```

## Architecture

```
app/
├── __init__.py
├── main.py              # FastAPI app entry point, lifespan, CORS, router registration
├── config.py            # Pydantic Settings (reads from .env / environment)
├── database.py          # Lazy AsyncEngine, async_session_factory, Base (avoids SQLite URI conflict)
├── deps.py              # Dependency injection: get_current_user, require_admin
├── envelope.py          # Unified {data, error} envelope + global exception handlers
├── models/              # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── base.py          # TimestampMixin (id, created_at, updated_at)
│   ├── auth.py          # User, RevokedToken, AuditLog
│   ├── question.py      # Question model (curriculum, subject, type, stem, options, etc.)
│   ├── question_embedding.py  # QuestionEmbedding model (VECTOR(1024))
│   ├── document.py      # Document model (title, content, source)
│   ├── embedding.py     # DocumentEmbedding model (VECTOR(1536))
│   └── taxonomy.py      # Curriculum, Subject, Topic, QuestionTypeMeta, LegalArticle, QuestionVersion
├── repositories/        # Data access layer (all SQL, parametrized, no business logic)
│   ├── __init__.py
│   ├── question_repo.py
│   └── taxonomy_repo.py
├── routers/             # Thin route handlers (I/O validation only, no SQL/business logic)
│   ├── __init__.py
│   ├── health.py        # GET /api/health
│   ├── auth.py          # POST /auth/login, /auth/logout, GET /auth/me
│   ├── questions.py     # CRUD + import + export for questions
│   ├── taxonomy.py      # CRUD for curricula, subjects, topics
│   ├── question_types.py # Read/update question type metadata
│   └── analysis.py      # GET /questions/{id}/analysis, /similar, AI breakdown
├── schemas/             # Pydantic request/response schemas
│   ├── __init__.py
│   ├── auth.py          # LoginRequest, LoginResponse, UserResponse
│   ├── question.py      # QuestionBase, QuestionCreate, QuestionUpdate, QuestionResponse, etc.
│   └── taxonomy.py      # Curriculum, Subject, Topic, QuestionTypeMeta schemas
├── security/            # Auth & security modules
│   ├── __init__.py
│   ├── jwt.py           # JWT create/decode access & refresh tokens
│   ├── passwords.py     # bcrypt hash/verify
│   └── rate_limit.py    # IP-based rate limiting middleware
├── services/            # Business logic + transaction boundaries
│   ├── __init__.py
│   ├── question_service.py
│   ├── analysis_service.py
│   └── llm.py           # LLM client (DeepSeek)
├── alembic/             # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 0001_create_questions_and_embeddings.py
│       ├── 0002_add_taxonomy.py          # Curricula, subjects, topics, question_types, legal_articles, question_versions
│       └── 0003_add_indexes.py           # Performance indexes
└── scripts/ingest/      # Question bank ingestion pipeline
    ├── parse_fakao_markdown.py  # Parse exam papers
    ├── normalize.py             # Normalize to standard format
    ├── classify.py              # Classify into taxonomy
    ├── seed_questions.py        # Seed into database
    └── embed_worker.py          # Generate embeddings
```

### Data Models

**Auth models** (milestone B3):
- `users`: UUID PK, email (unique), password_hash (bcrypt), role (student/admin), display_name, is_active
- `revoked_tokens`: jti (JWT ID), expires_at — logout blacklist
- `audit_logs`: actor_user_id, action, entity_type, entity_id, payload (JSONB), ip

**Question** (table: `questions`)
- Curriculum categorization: `curriculum`, `subject`, `topic_path` (hierarchical array)
- Metadata: `difficulty` (1-5), `type` (enum: multiple_choice, single_choice, true_false, fill_blank, short_answer, essay, code, matching, ordering)
- Content: `stem` (question body), `options` (JSONB), `answer`, `rubric` (JSONB), `solution`
- Extensions: `source_year`, `is_indeterminate`, `cited_articles` (UUID[]), `deleted_at` (soft delete)
- Variants: `variants` (array of UUIDs for linked questions)
- Source: `source_origin`
- Timestamps: `created_at`, `updated_at`

**QuestionEmbedding** (table: `question_embeddings`)
- Links to `questions.id` via FK (CASCADE delete)
- `embedding`: pgvector VECTOR(1024) — 1024-dimensional vector
- `model_name`: identifier for the embedding model used

**Taxonomy** (table: `curricula`, `subjects`, `topics`, `question_types`, `legal_articles`, `question_versions`)
- Hierarchical: Curriculum → Subjects → Topics (tree with parent_id)
- Question versions for audit trail on edits
- Legal articles with subject, article_number, content, interpretation, high-freq flag

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
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60`                                                           | Access token expiry        |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7`                                                              | Refresh token expiry       |
| `CORS_ORIGINS`             | `["http://localhost:3000"]`                                      | Allowed CORS origins       |
| `LLM_API_KEY`              | —                                                                | DeepSeek API key           |
| `LLM_BASE_URL`             | `https://api.deepseek.com/v1`                                    | LLM endpoint               |
| `LLM_MODEL`                | `deepseek-chat`                                                  | Default LLM model          |

## API Endpoints (all prefixed with `/api/v1`)

All responses use unified envelope `{ data, error }`. Error format: `{ code, message, field? }`.

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

## Security

- **JWT + httpOnly cookies**: Tokens stored in httpOnly, Secure, SameSite=Lax cookies. Access token (short TTL, configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`) + Refresh token (long TTL, configurable via `REFRESH_TOKEN_EXPIRE_DAYS`).
- **Password hashing**: bcrypt via passlib. Verification returns generic error (no username enumeration).
- **Token revocation**: Logout writes JWT `jti` to `revoked_tokens` table with TTL-based auto-cleanup.
- **Rate limiting**: Per-IP rate limiting with configurable window/burst. Login endpoint uses stricter limits to prevent brute force.
- **Authorization**: `require_admin` dependency on all `/admin/*` write operations. All user-data queries scoped by `user_id`.
- **Input validation**: All input validated via Pydantic v2 with strict schemas. SQL injection prevented via SQLAlchemy parameterized queries (no f-string SQL).
- **API Envelope**: All errors return standardized `{ error: { code, message, field? } }` with codes like `AUTH_REQUIRED`, `FORBIDDEN`, `NOT_FOUND`, `VALIDATION_FAILED`, `CONFLICT`, `RATE_LIMITED`, `INTERNAL`.

## Implementation Progress

| Milestone | Status      | Description                                  |
|-----------|-------------|----------------------------------------------|
| B1        | ✅ Done     | Layered skeleton + envelope + exception handlers |
| B2        | ✅ Done     | Question bank + taxonomy + search            |
| B3        | ✅ Done     | Auth (JWT/cookie/RBAC/rate limiting/audit)   |
| B4–B8     | 📋 Planned  | See root README and implementation plan      |

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
```

### Running Tests

```bash
# Run all tests (requires a PostgreSQL + pgvector instance)
pytest -v

# Run import verification (no DB required)
python verify_imports.py
```

### Verifying Imports

A standalone import verification script (`verify_imports.py`) checks all modules can be imported and auth primitives work end-to-end:
- Config loads from environment
- Password hash/verify round-trip
- JWT create/decode for access and refresh tokens
- All ORM models import successfully
- Pydantic schemas validate correctly
- Envelope format is correct
- Dependency injection functions are callable
