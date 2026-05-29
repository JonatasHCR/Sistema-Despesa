from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.settings import Settings


_settings = Settings()

# Argon2 é o algoritmo padrão para novas senhas; o BcryptHasher fica na lista
# apenas para verificar hashes antigos (bcrypt) já gravados no banco. No login,
# `verify_and_update_password` regrava esses hashes em Argon2 automaticamente.
_password_hash = PasswordHash((
    Argon2Hasher(),
    BcryptHasher(),
))


def hash_password(plain_password: str) -> str:
    return _password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return _password_hash.verify(plain_password, hashed_password)
    except Exception:
        return False


def verify_and_update_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, str | None]:
    """Verifica a senha e, se o hash usar um esquema antigo (bcrypt), devolve
    um novo hash em Argon2 no segundo item da tupla (caso contrário, None)."""
    try:
        return _password_hash.verify_and_update(plain_password, hashed_password)
    except Exception:
        return False, None


def create_access_token(subject: str | int, extra_claims: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": now + timedelta(minutes=_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, _settings.JWT_SECRET_KEY, algorithm=_settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, _settings.JWT_SECRET_KEY, algorithms=[_settings.JWT_ALGORITHM])
