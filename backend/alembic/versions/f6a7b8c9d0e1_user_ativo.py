"""Marca de acesso: tb_users.ativo

Espelha o grupo do Keycloak dentro do sistema. Quem perde o acesso fica
`ativo = false` — a linha NÃO é removida, porque há FKs de tb_despesas,
tb_notificacao_config e tb_despesa_destinatarios apontando para ela.

Todo mundo que já existe entra como ativo: a coluna nasce com default true, e
quem tiver perdido o acesso será marcado na primeira requisição que fizer.

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, Sequence[str], None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tb_users",
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_column("tb_users", "ativo")
