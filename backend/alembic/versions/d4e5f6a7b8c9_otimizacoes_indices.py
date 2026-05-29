"""otimizacoes de indices e restricoes

- Remove ix_tb_users_id e ix_tb_despesas_id (PK ja e indexada pelo Postgres)
- Remove ix_tb_users_nome (duplica uq_tb_users_nome, que ja e um indice B-tree)
- Adiciona ix_tb_despesas_vencimento (usado em ORDER BY e WHERE nos digests)
- Torna tb_users.email NOT NULL (modelo ORM ja declarava nullable=False)

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove índices redundantes
    op.drop_index("ix_tb_users_id", table_name="tb_users", if_exists=True)
    op.drop_index("ix_tb_despesas_id", table_name="tb_despesas", if_exists=True)
    # ix_tb_users_nome é redundante: uq_tb_users_nome (unique constraint) já é B-tree index
    op.drop_index("ix_tb_users_nome", table_name="tb_users", if_exists=True)

    # Índice em vencimento: ORDER BY e WHERE vencimento <= X em toda listagem e digest
    op.create_index("ix_tb_despesas_vencimento", "tb_despesas", ["vencimento"])

    # valor NUMERIC → NUMERIC(10,2): impõe precisão monetária (máx. 10 dígitos, 2 decimais)
    op.alter_column(
        "tb_despesas", "valor",
        existing_type=sa.Numeric(),
        type_=sa.Numeric(10, 2),
        nullable=False,
    )

    # email NOT NULL — garante consistência com o modelo ORM
    # Preenche eventuais NULLs antes de impor a restrição (bancos antigos)
    op.execute(
        "UPDATE tb_users SET email = 'sem_email_' || id || '@placeholder.invalid' "
        "WHERE email IS NULL"
    )
    op.alter_column("tb_users", "email", existing_type=sa.String(255), nullable=False)


def downgrade() -> None:
    op.alter_column("tb_users", "email", existing_type=sa.String(255), nullable=True)
    op.alter_column(
        "tb_despesas", "valor",
        existing_type=sa.Numeric(10, 2),
        type_=sa.Numeric(),
        nullable=False,
    )
    op.drop_index("ix_tb_despesas_vencimento", table_name="tb_despesas")
    op.create_index("ix_tb_users_nome", "tb_users", ["nome"])
    op.create_index("ix_tb_despesas_id", "tb_despesas", ["id"])
    op.create_index("ix_tb_users_id", "tb_users", ["id"])
