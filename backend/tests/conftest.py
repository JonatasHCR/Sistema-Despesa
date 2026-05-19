import os
import asyncio

# Variáveis de ambiente necessárias antes de qualquer import de app.
# O engine "real" é criado no import de app.core.database mas nunca usado nos
# testes (o get_db é sobrescrito), então basta uma URL válida.
os.environ["ENGINE"] = "postgresql+asyncpg"
os.environ["DB_USER"] = "test"
os.environ["DB_PASSWORD"] = "test"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-only-for-pytest"
os.environ["RATE_LIMIT_ENABLED"] = "0"
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "*"

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import StaticPool
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager

from main import app
from app.core.database import Base, get_db


DATABASE_URL = "sqlite+aiosqlite:///:memory:"
BASE_URL = "http://127.0.0.1:8000"


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_db(async_engine, event_loop):
    async with async_engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        session_factory = sessionmaker(
            bind=conn, class_=AsyncSession, expire_on_commit=False
        )

        AsyncScopedSession = async_scoped_session(session_factory, scopefunc=asyncio.current_task)

        async with AsyncScopedSession() as session:
            yield session
            await AsyncScopedSession.remove()


@pytest_asyncio.fixture
async def async_client(async_db):
    async def override_get_db():
        async with async_db as db:
            try:
                yield db
                await db.commit()
            except:
                await db.rollback()
                raise
            finally:
                await db.close()

    app.dependency_overrides[get_db] = override_get_db
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as client:
            yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth(async_client):
    """Cria um usuário, faz login e retorna user, token e headers prontos."""
    credentials = {"nome": "usuario teste", "senha": "senha123"}
    create_response = await async_client.post(
        "/users/",
        json={**credentials, "email": "teste@gmail.com"},
    )
    assert create_response.status_code == 201, create_response.text
    user = create_response.json()

    login_response = await async_client.post("/auth/login", json=credentials)
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["access_token"]

    return {
        "user": user,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }
