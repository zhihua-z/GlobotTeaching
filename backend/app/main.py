from contextlib import asynccontextmanager
from sqlalchemy import text
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, get_engine
from app.envelope import register_exception_handlers
from app.routers import health, questions, taxonomy, question_types, analysis, auth, prompts, pipeline, review, evals

# Import all models so Base.metadata.create_all picks them up
from app.models.question import Question
from app.models.question_embedding import QuestionEmbedding
from app.models.taxonomy import (
    Curriculum,
    Subject,
    Topic,
    QuestionTypeMeta,
)
from app.models.auth import User, RevokedToken, AuditLog
from app.models.prompt import PromptTemplate, PromptTemplateVersion
from app.models.pipeline import PipelineRun, QuestionDraft
from app.models.evals import EvalSet, EvalCase, EvalRun


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: enable extensions and create tables (for dev convenience; use Alembic in production)
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.run_sync(Base.metadata.create_all)
    # Seed default prompt templates
    from app.database import AsyncSessionLocal
    from app.services.prompt_service import PromptService
    async with AsyncSessionLocal() as session:
        async with session.begin():
            prompt_svc = PromptService(session)
            await prompt_svc.seed_defaults()
    yield
    # Shutdown
    engine = get_engine()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router)
app.include_router(questions.router)
app.include_router(taxonomy.router)
app.include_router(question_types.router)
app.include_router(analysis.router)
app.include_router(auth.router)
app.include_router(prompts.router)
app.include_router(pipeline.router)
app.include_router(review.router)
app.include_router(evals.router)

# Register exception handlers for unified envelope errors
register_exception_handlers(app)


@app.get("/")
async def root():
    return {"message": "Globot Teaching API"}