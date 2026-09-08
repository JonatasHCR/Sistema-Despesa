"""tb_users.admin — dono da tela de Administração

Único papel que este sistema conhece. Existe para a tela de Administração
(backup, limpeza, restauração) ter um responsável; NÃO governa despesas, que
seguem compartilhadas no setor.

Ninguém nasce admin: a coluna entra com default false. Promova pelo script
`promover_admin.py`, que é a única porta de entrada — de propósito, para o
primeiro admin não poder ser criado pela própria tela.

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tb_users",
        sa.Column("admin", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("tb_users", "admin")
