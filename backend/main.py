from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.version_1.endpoints.despesa import DespesaEndpoint
from app.api.version_1.endpoints.user import UserEndpoint
from app.api.version_1.endpoints.auth import AuthEndpoint

from app.core.database import Base, engine

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield  # app running

app = FastAPI(
    title="Organizador de Finanças API",
    docs_url="/documentation",
    redoc_url="/recaudacao",
    openapi_url="/api/openapi.json",
    openapi_tags=[
        {"name": "User", "description": "Operações com Usuários"},
        {"name": "Despesa", "description": "Operações com Despesas"},
        {"name": "Auth", "description": "Operações de Autenticação"},
    ],
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(UserEndpoint().router)
app.include_router(DespesaEndpoint().router)
app.include_router(AuthEndpoint().router)
