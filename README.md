# Sistema Despesa — SISTEMA RADAR

Gerenciador de despesas pessoais/familiares com painel web, API e um **agente de notificações nativo do Windows** que avisa sobre contas vencendo ou vencidas. A linguagem do domínio é **português** (no código, no banco e na interface).

O projeto tem três partes:

| Parte | Stack | O que faz |
|-------|-------|-----------|
| **backend/** | FastAPI + SQLAlchemy 2 (async) + Alembic + PostgreSQL | API REST: usuários, despesas, autenticação JWT e configuração de notificações |
| **frontend/** | Next.js 15 (App Router) + TypeScript + Tailwind + shadcn/ui | Painel web: dashboard, cadastro/edição de despesas, relatórios, perfil |
| **agent/** | Python (PyInstaller → `.exe`) | Roda em cada máquina da rede e mostra um *toast* do Windows com o digest diário de vencimentos |

---

## Visão geral

O usuário cadastra despesas (`nome`, `tipo`, `valor`, `vencimento`, `status`, `descrição`). O dashboard classifica cada despesa em tempo real como **vencida / vence em breve / a vencer / quitada**, combinando a data de vencimento com o status armazenado (`P` = Pendente, `Q` = Quitada).

Cada despesa pode ter **destinatários** — usuários que devem ser avisados sobre ela. Cada usuário configura suas preferências de notificação em **Meu Perfil → Notificações** (ativo/inativo, dias de antecedência, avisar vencidas). O agente de Windows consulta o backend uma vez por dia e exibe um toast com as despesas dentro da janela configurada.

---

## Arquitetura

### Backend (camadas)

Estritamente em camadas, com genéricos propagando os tipos. Adicionar um novo recurso significa clonar essa pilha:

```
api/version_1/endpoints/<x>.py   Router FastAPI; instancia o Service por request com AsyncSession injetada
service/<x>.py                   estende BaseService[Repo, InputSchema, OutputSchema]; orquestra + valida
repository/<x>.py                estende BaseRepository[Model]; queries SQLAlchemy
model/<x>.py                     modelo ORM SQLAlchemy (Base de app.core.database)
schema/<x>.py                    schemas Pydantic (Input/Output, e Update se houver edição parcial)
```

Os routers são registrados em [`backend/main.py`](backend/main.py). Há rate limiting (`slowapi`) e CORS configurável por env.

**Modelos principais:**
- `tb_users` — `id`, `nome` (único), `email` (único), `senha` (hash bcrypt).
- `tb_despesas` — despesa, com `status` restrito a `P`/`Q` por CHECK constraint e FK para o usuário dono.
- `tb_notificacao_config` — preferências de notificação por usuário.
- `tb_despesa_destinatarios` — quem é avisado de cada despesa (N:N entre despesa e usuário).

**Autenticação:** `POST /auth/login` devolve `{access_token, token_type, user}`. JWT HS256 com segredo em `JWT_SECRET_KEY`. Todas as rotas exigem `Authorization: Bearer <token>`, exceto `POST /users/` (cadastro) e `POST /auth/login`. A posse é validada em `PUT/DELETE` de usuários e despesas; `POST /despesas/` deriva o `user_id` do token.

**Migrações:** Alembic é a fonte única do schema em container/produção (`migrations.sh` roda `alembic upgrade head` antes do uvicorn). O autogenerate está **desligado** (`target_metadata = None`) — ao mudar um modelo, escreva a revisão à mão.

### Frontend

App Router em [`frontend/src/app/`](frontend/src/app/): `/` (dashboard), `/login`, `/signup`, `/profile`, `/reports`, `/expenses/new`, `/expenses/[id]/edit`. A maioria das páginas é `'use client'`.

Todas as chamadas HTTP passam por [`frontend/src/lib/api.ts`](frontend/src/lib/api.ts). A URL base é escolhida em tempo de chamada: SSR usa `INTERNAL_API_BASE_URL` (nome de serviço Docker `backend`); o navegador usa `NEXT_PUBLIC_API_BASE_URL` (precisa ser alcançável a partir do host). O token e a sessão ficam em `localStorage`; `apiFetch` injeta o bearer e redireciona para `/login` em 401.

### Agente de notificações

Veja [`agent/README.md`](agent/README.md) para o passo a passo de build, instalação e agendamento. Resumo: gera-se `despesa-agent.exe`, copia-se para cada máquina junto de um `config.json` (URL do backend + login do usuário), e agenda-se via Agendador de Tarefas do Windows. A regra de "o que avisar" mora no backend; o agente só lê o digest e mostra o toast.

---

## API (resumo)

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/users/` | Cadastro (público) |
| `GET/PUT/DELETE` | `/users/{id}` | Gerenciar usuário (posse exigida em PUT/DELETE) |
| `POST` | `/auth/login` | Login → JWT (público) |
| `GET` | `/despesas/?limit=&offset=` | Lista despesas (já com `user_nome` no join) |
| `POST` | `/despesas/` | Cria despesa (user_id vem do token) |
| `GET/PUT/DELETE` | `/despesas/{id}` | Gerenciar despesa (posse exigida) |
| `GET/PUT` | `/notificacoes/config` | Preferências de notificação do usuário |
| `GET` | `/notificacoes/digest` | Digest de vencimentos do usuário (consumido pelo agente) |

Docs com o backend no ar: Swagger em `http://localhost:8000/documentation`, ReDoc em `/recaudacao`.

---

## Como rodar

### Stack completa (Docker)

Copie `.env.exemplo` para `.env` e ajuste. Variáveis principais:

- `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB`
- `INTERNAL_API_BASE_URL` — alvo de fetch no servidor (ex.: `http://backend:8000`)
- `NEXT_PUBLIC_API_BASE_URL` — alvo de fetch no navegador (URL alcançável pelo host)
- `JWT_SECRET_KEY` — segredo do JWT
- `CORS_ALLOWED_ORIGINS` — origens permitidas, separadas por vírgula (default `http://localhost:3000`)

```bash
docker compose up --build
```

Sobe `db` (Postgres 17), `backend` (porta 8000, espera o db, roda migrações, então uvicorn) e `frontend` (porta 3000, `npm run dev`).

### Backend isolado (Poetry — rode em `backend/`)

```bash
poetry install                          # venv + deps (inclui grupo dev)
poetry run uvicorn main:app --reload    # dev server :8000  (ou: poetry run task run)
poetry run alembic upgrade head         # aplica migrações
poetry run alembic revision -m "msg"    # nova migração (autogenerate OFF — escreva à mão)
poetry run pytest                       # testes (markers: service, routers, integration)
poetry run task lint                    # ruff check  (task fix / task format)
```

### Frontend isolado (rode em `frontend/`)

```bash
npm run dev          # next dev --turbopack :3000
npm run build        # usa sintaxe bash (NODE_ENV=...) — use WSL/bash ou Docker, não PowerShell puro
npm run typecheck    # tsc --noEmit  (o build ignora erros de TS/ESLint — rode isto à parte)
npm run lint         # next lint
```

> O `next.config.ts` define `typescript.ignoreBuildErrors: true` e `eslint.ignoreDuringBuilds: true`, então `npm run build` **não** pega erros de tipo ou lint — sempre rode `npm run typecheck` e `npm run lint` antes de considerar uma mudança pronta.

---

## Convenções

- Domínio em **português** no código e no banco (`nome`, `senha`, `vencimento`, `tb_despesas`, `tb_users`). Mantenha novos identificadores consistentes.
- `despesa.descricao` tem no máximo 20 caracteres e default `"PARCELA ÚNICA"` — metadados de parcelamento vivem nesse campo de texto, não em tabela separada.
- O input de moeda no frontend é formatado por locale (`.` milhar, `,` decimal); `formatCurrencyValueForAPI` normaliza antes do POST/PUT.
- Os testes constroem o schema com SQLite em memória (`tests/conftest.py`); migrações Alembic valem para container/produção.
</content>
</invoke>
