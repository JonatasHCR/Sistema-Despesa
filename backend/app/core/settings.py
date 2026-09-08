
from os.path import dirname, join
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = dirname(dirname(dirname(__file__)))


class Settings(BaseSettings):
    ENGINE: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    # --- OIDC / Keycloak ---------------------------------------------------
    # Quem emite token e o Keycloak; aqui so validamos, com a chave publica
    # dele. Nao ha segredo de assinatura para guardar.
    OIDC_ISSUER: str

    # O `aud` do access token. Cuidado: por padrao o Keycloak emite
    # aud="account", NAO o client_id — validar contra o client rejeitaria todo
    # token. O realm tem um audience mapper que injeta este valor.
    OIDC_AUDIENCE: str = "despesa-api"

    # Grupo exigido para entrar neste sistema. Sem esta checagem o
    # provisionamento automatico abriria a despesa para todo o realm.
    OIDC_REQUIRED_GROUP: str = "/apps/despesa"

    # A conta mestra: UM email, definido no infra/.env e propagado aos tres
    # sistemas, que entra como administrador aqui sem precisar do
    # `promover_admin.py`. Existe para nao ser preciso manter tres contas so
    # para administrar.
    #
    # Nao e papel do Keycloak nem grupo: ser admin do console do Keycloak nao
    # da poder nenhum aqui, e nenhum grupo concede isto. E so este endereco.
    # Vazio (o padrao) = nao existe conta mestra.
    ADMIN_MESTRE_EMAIL: str = ""

    model_config = SettingsConfigDict(
        env_file=join(BASE_DIR, f".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def database_url(self) -> str:
        return f"{self.ENGINE}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def oidc_jwks_url(self) -> str:
        return f"{self.OIDC_ISSUER.rstrip('/')}/protocol/openid-connect/certs"

    @property
    def oidc_authorization_url(self) -> str:
        return f"{self.OIDC_ISSUER.rstrip('/')}/protocol/openid-connect/auth"

    @property
    def oidc_token_url(self) -> str:
        return f"{self.OIDC_ISSUER.rstrip('/')}/protocol/openid-connect/token"
