from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import Settings
from app.db.base import Base
from app.models.user import User

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


@pytest.fixture(scope="session")
def event_loop_policy() -> asyncio.AbstractEventLoopPolicy:
    if sys.platform == "win32":
        return asyncio.WindowsSelectorEventLoopPolicy()
    return asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture
async def async_engine() -> AsyncEngine:
    pytest.importorskip("asyncpg")
    settings = Settings()
    database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
        poolclass=NullPool,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def prepare_database(async_engine: AsyncEngine) -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture
async def async_session(async_engine: AsyncEngine) -> AsyncSession:
    maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
    async with maker() as session:
        yield session
        await session.rollback()


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    from app.main import app
    yield
    app.dependency_overrides = {}


@pytest_asyncio.fixture
async def client(async_session: AsyncSession):
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    from app.db.database import get_db

    app.dependency_overrides[get_db] = lambda: async_session

    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def authenticated_test_user(async_session: AsyncSession) -> User:
    from app.core.security import get_password_hash
    
    user = User(
        name="Test User",
        email="test_auth@example.com",
        password_hash=get_password_hash("password123"),
        is_active=True,
    )
    async_session.add(user)
    await async_session.flush()
    return user


@pytest.fixture
def jwt_token(authenticated_test_user: User) -> str:
    from app.core.security import create_access_token
    return create_access_token(subject=str(authenticated_test_user.id))


@pytest.fixture
def auth_header(jwt_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {jwt_token}"}

