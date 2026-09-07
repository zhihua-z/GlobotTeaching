"""Pytest fixtures for test database and test client."""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.database import Base, get_db
from app.main import app

# Use PostgreSQL for tests (required for ARRAY, VECTOR types used in models)
# Connect as current user on localhost with test database
TEST_DATABASE_URL = "postgresql+asyncpg://heizi:@localhost:5432/globot_test"

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    
    # Enable pgvector extension and create all tables
    async with engine.begin() as conn:
        from sqlalchemy import text
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

        # Seed question_types (required by tests)
        from app.models.taxonomy import QuestionTypeMeta
        question_types = [
            QuestionTypeMeta(code="single_choice", label_en="Single Choice", label_zh="单选题", requires_options=True, requires_rubric=False),
            QuestionTypeMeta(code="multiple_choice", label_en="Multiple Choice", label_zh="多选题", requires_options=True, requires_rubric=False),
            QuestionTypeMeta(code="short_answer", label_en="Short Answer", label_zh="简答题", requires_options=False, requires_rubric=True),
            QuestionTypeMeta(code="essay", label_en="Essay", label_zh="论述题", requires_options=False, requires_rubric=True),
            QuestionTypeMeta(code="true_false", label_en="True/False", label_zh="判断题", requires_options=False, requires_rubric=False),
            QuestionTypeMeta(code="fill_blank", label_en="Fill in the Blank", label_zh="填空题", requires_options=False, requires_rubric=False),
            QuestionTypeMeta(code="matching", label_en="Matching", label_zh="匹配题", requires_options=True, requires_rubric=False),
            QuestionTypeMeta(code="ordering", label_en="Ordering", label_zh="排序题", requires_options=True, requires_rubric=False),
        ]
        from sqlalchemy import insert as sa_insert
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        for qt in question_types:
            stmt = pg_insert(QuestionTypeMeta).values(
                code=qt.code,
                label_en=qt.label_en,
                label_zh=qt.label_zh,
                requires_options=qt.requires_options,
                requires_rubric=qt.requires_rubric,
            ).on_conflict_do_nothing()
            await conn.execute(stmt)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    # Clean up all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Test client with overridden DB dependency."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()