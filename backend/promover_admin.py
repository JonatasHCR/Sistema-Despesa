"""Concede (ou remove) o papel de administrador deste sistema.

É a ÚNICA porta de entrada para o papel — de propósito. Se a própria tela de
Administração pudesse promover, o primeiro admin teria de nascer de algum lugar,
e qualquer pessoa com acesso à tela poderia se promover.

O papel é local e vale só para a tela de Administração (backup, limpeza,
restauração). Não muda nada em despesas.

Uso, a partir da pasta backend/:
    python promover_admin.py fulano@empresa.com
    python promover_admin.py fulano@empresa.com --remover
"""

import argparse
import asyncio
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import Settings
from app.model.user import User


async def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("email")
    p.add_argument("--remover", action="store_true", help="tira o papel em vez de conceder")
    args = p.parse_args()

    email = args.email.strip().lower()
    settings = Settings()
    engine = create_async_engine(settings.database_url())
    Sessao = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with Sessao() as sessao:
            user = (
                await sessao.execute(select(User).where(User.email == email))
            ).scalar_one_or_none()

            if user is None:
                print(f"'{email}' ainda não existe aqui.")
                print()
                print("A conta local nasce no primeiro login: peça à pessoa para")
                print("entrar uma vez pelo portal e rode este comando de novo.")
                return 1

            user.admin = not args.remover
            await sessao.commit()

            acao = "removido de" if args.remover else "concedido a"
            print(f"Papel de administrador {acao} {email}.")
        return 0
    finally:
        await engine.dispose()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
