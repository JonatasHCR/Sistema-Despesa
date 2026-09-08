import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.settings import Settings
from app.model.user import User
from app.repository.user import UserRepository


_settings = Settings()

# Só documenta o fluxo no Swagger: quem emite o token é o Keycloak. O front
# fala com o proxy do Next, que anexa o header a partir do cookie.
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=_settings.oidc_authorization_url,
    tokenUrl=_settings.oidc_token_url,
    auto_error=True,
)

# Preguiçoso: nada é baixado no import, só na primeira validação.
_jwks_client = jwt.PyJWKClient(_settings.oidc_jwks_url)


def _nome_das_claims(payload: dict) -> str:
    return (
        payload.get("name")
        or payload.get("preferred_username")
        or payload.get("email")
        or ""
    ).strip()


async def _provisionar(
    repository: UserRepository, payload: dict, sub: str, email: str
) -> User:
    """Cria a conta local no primeiro acesso (JIT).

    `tb_users.nome` é UNIQUE, então o email desempata nomes iguais.
    """
    nome = _nome_das_claims(payload) or email
    if await repository.get_by_username(nome) is not None:
        nome = email

    try:
        return await repository.create(nome=nome, email=email, external_id=sub)
    except IntegrityError:
        # Corrida entre duas requisições do mesmo recém-chegado.
        existente = await repository.find_by_external_id(sub)
        if existente is None:
            raise
        return existente


def _e_mestre(email: str) -> bool:
    """A conta mestra: um unico email, vindo do infra/.env.

    Nao e grupo nem papel do Keycloak — ser admin do console nao da poder algum
    aqui. E so este endereco, admin dos tres sistemas ao mesmo tempo.
    """
    mestre = (_settings.ADMIN_MESTRE_EMAIL or "").strip().lower()
    return bool(mestre) and email == mestre


def _sem_acesso() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Você não tem acesso ao sistema de despesas. "
        "Peça a liberação ao administrador.",
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Valida o token do Keycloak e devolve o usuário local correspondente.

    Ponto único de autenticação do serviço.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        chave = _jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            chave.key,
            algorithms=["RS256"],
            issuer=_settings.OIDC_ISSUER,
            audience=_settings.OIDC_AUDIENCE,
        )
    except (jwt.PyJWTError, jwt.PyJWKClientError):
        raise credentials_error

    sub = payload.get("sub")
    email = (payload.get("email") or "").strip().lower()
    if not sub or not email:
        raise credentials_error

    # A mestra entra sem grupo: se dependesse, tirar a si mesmo de um grupo
    # trancaria a porta de quem conserta.
    mestre = _e_mestre(email)
    tem_acesso = mestre or (
        _settings.OIDC_REQUIRED_GROUP in (payload.get("groups") or [])
    )
    repository = UserRepository(db)

    # 1) já vinculado — o caminho normal, depois do primeiro login
    user = await repository.find_by_external_id(sub)

    # 2) conta anterior ao SSO: casa por email e grava o vínculo, preservando
    #    o id e todas as FKs.
    if user is None:
        user = await repository.find_by_email(email)
        if user is not None:
            user = await repository.update(user.id, external_id=sub)

    if user is not None:
        # Espelha o acesso do Keycloak. Nunca apagada: há despesas e
        # notificações apontando para ela.
        if user.ativo != tem_acesso:
            user = await repository.update(user.id, ativo=tem_acesso)

        # A cada login, para trocar o ADMIN_MESTRE_EMAIL valer sem script.
        if mestre and not user.admin:
            user = await repository.update(user.id, admin=True)

        if not tem_acesso:
            raise _sem_acesso()
        return user

    # 3) primeira vez. Sem grupo não provisiona: cadastro não pode ser efeito
    #    colateral de um acesso negado.
    if not tem_acesso:
        raise _sem_acesso()

    novo = await _provisionar(repository, payload, sub, email)
    if mestre:
        novo = await repository.update(novo.id, admin=True)
    return novo


async def get_current_admin(
    user: User = Depends(get_current_user),
) -> User:
    """Exige o papel local de administrador.

    `tb_users.admin` existe só para a tela de Administração; não governa
    despesas. Vem do `promover_admin.py` ou da conta mestra — nunca da tela,
    senão quem chegasse nela se promoveria.
    """
    if not user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta área é restrita aos administradores do sistema.",
        )
    return user
