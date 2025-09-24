import os

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import StaticPool
from httpx import AsyncClient
from asgi_lifespan import LifespanManager

from main import app
from app.core.database import Base, get_db


os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "*"

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
BASE_URL = "http://127.0.0.1:8000"


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
async def async_db(async_engine):
    async with async_engine.connect() as conn:
        
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
        AsyncSessionLocal = sessionmaker(
            bind=conn, class_=AsyncSession, expire_on_commit=False
        )

        async with AsyncSessionLocal() as session:
            yield session
        



@pytest_asyncio.fixture
async def async_client(async_db):
    app.dependency_overrides[get_db] = lambda: async_db
    async with LifespanManager(app):
        async with AsyncClient(base_url=BASE_URL) as client:
            yield client
