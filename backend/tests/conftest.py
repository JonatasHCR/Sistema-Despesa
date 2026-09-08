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
# Não há mais segredo de assinatura: os testes cunham tokens RS256 com uma
# chave própria e trocam o PyJWKClient (ver tests/support/oidc.py).
os.environ["OIDC_ISSUER"] = "http://keycloak-de-teste:8080/realms/ufc"
os.environ["OIDC_AUDIENCE"] = "despesa-api"
os.environ["OIDC_REQUIRED_GROUP"] = "/apps/despesa"
os.environ["RATE_LIMIT_ENABLED"] = "0"
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "*"

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import StaticPool
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager

from main import app
from app.api.version_1 import dependencies
from app.core.database import Base, get_db
from tests.support import oidc


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


@pytest.fixture(autouse=True)
def _sem_keycloak(monkeypatch):
    """Troca o cliente de JWKS pelo falso — nenhum teste toca a rede."""
    monkeypatch.setattr(dependencies, "_jwks_client", oidc.JWKClientFalso())


async def _entrar(async_client, sub: str, email: str, nome: str):
    """Faz a primeira requisição autenticada, que é o que provisiona a conta.

    Não há mais cadastro nem login: a conta local nasce no primeiro token válido
    (JIT), exatamente como em produção. Por isso a fixture entra pelo GET
    /users/ em vez de criar o usuário à mão — assim o teste exercita o caminho
    de provisionamento de verdade.
    """
    headers = {"Authorization": f"Bearer {oidc.cunhar_token(sub, email, nome)}"}
    resposta = await async_client.get(f"/users/email/{email}", headers=headers)
    assert resposta.status_code == 200, resposta.text
    return {"user": resposta.json(), "token": headers["Authorization"], "headers": headers}


@pytest_asyncio.fixture
async def auth(async_client):
    """Usuário autenticado pelo Keycloak, provisionado na primeira chamada."""
    return await _entrar(
        async_client,
        sub="11111111-1111-1111-1111-111111111111",
        email="teste@gmail.com",
        nome="usuario teste",
    )


@pytest_asyncio.fixture
async def outro_auth(async_client):
    """Um segundo usuário, para os testes de permissão entre contas."""
    return await _entrar(
        async_client,
        sub="22222222-2222-2222-2222-222222222222",
        email="outro@gmail.com",
        nome="outro",
    )
