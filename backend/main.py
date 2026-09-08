from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.version_1.endpoints.despesa import DespesaEndpoint
from app.api.version_1.endpoints.user import UserEndpoint
from app.api.version_1.endpoints.manutencao import ManutencaoEndpoint
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
        {"name": "Notificacao", "description": "Configuração e digest de notificações"},
        {"name": "Manutencao", "description": "Backup, restauração e limpeza (só admin)"},
    ],
)

# Rate limiter (slowapi)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Sem CORS: nenhum navegador fala com esta API. O front chama `/api` no mesmo
# servidor Next, que repassa por dentro da rede do Docker; o agente Windows não
# é navegador e não faz preflight. Manter o middleware só daria a impressão de
# que a API é chamada de origens cruzadas.

app.include_router(UserEndpoint().router)
app.include_router(DespesaEndpoint().router)
app.include_router(NotificacaoEndpoint().router)
app.include_router(ManutencaoEndpoint().router)
