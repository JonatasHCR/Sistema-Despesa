from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.database import engine, Base
from app.api.version_1.endpoints.despesa import DespesaEndpoint
from app.api.version_1.endpoints.user import UserEndpoint


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Organizador de Finanças API",
    docs_url="/documentation",
    redoc_url="/recaudacao",
    openapi_url="/api/openapi.json",
    openapi_tags=[
        {"name": "User", "description": "Operações com Usuários"},
        {"name": "Despesa", "description": "Operações com Despesas"},
    ],
    lifespan=lifespan,
)

app.include_router(UserEndpoint().router)
app.include_router(DespesaEndpoint().router)
