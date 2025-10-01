
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware


from app.core.database import engine, Base
from app.api.version_1.endpoints.despesa import DespesaEndpoint
from app.api.version_1.endpoints.user import UserEndpoint
from app.api.version_1.endpoints.auth import AuthEndpoint


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
)

origins = [
    "http://localhost",
    "http://localhost:9002",
    "http://127.0.0.1",
    "http://127.0.0.1:9002",
    "http://10.0.0.199",
    "http://10.0.0.199:9002",
    "http://10.0.0.199:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(UserEndpoint().router)
app.include_router(DespesaEndpoint().router)
app.include_router(AuthEndpoint().router)
