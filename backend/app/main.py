from contextlib import asynccontextmanager
from sqlalchemy import text
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import health, questions, taxonomy, question_types, analysis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: enable extensions and create tables (for dev convenience; use Alembic in production)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
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


@app.get("/")
async def root():
    return {"message": "Globot Teaching API"}