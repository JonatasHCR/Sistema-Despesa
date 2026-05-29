import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.version_1.endpoints.despesa import DespesaEndpoint
from app.api.version_1.endpoints.user import UserEndpoint
from app.api.version_1.endpoints.auth import AuthEndpoint
from app.api.version_1.endpoints.notificacao import NotificacaoEndpoint
from app.core.rate_limit import limiter


app = FastAPI(
    title="Organizador de Finanças API",
    docs_url="/documentation",
    redoc_url="/recaudacao",
    openapi_url="/api/openapi.json",
    openapi_tags=[
        {"name": "User", "description": "Operações com Usuários"},
        {"name": "Despesa", "description": "Operações com Despesas"},
        {"name": "Auth", "description": "Operações de Autenticação"},
        {"name": "Notificacao", "description": "Configuração e digest de notificações"},
    ],
)

# Rate limiter (slowapi)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

_allowed_origins_env = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000")
_allowed_origins = [o.strip() for o in _allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(UserEndpoint().router)
app.include_router(DespesaEndpoint().router)
app.include_router(AuthEndpoint().router)
app.include_router(NotificacaoEndpoint().router)
