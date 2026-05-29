"""notificacoes: config por usuario + destinatarios por despesa

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-22 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tb_notificacao_config",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "dias_antecedencia", sa.Integer(), nullable=False, server_default="5"
        ),
        sa.Column(
            "avisar_vencidas", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.PrimaryKeyConstraint("user_id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["tb_users.id"],
            name="fk_notif_config_user",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        comment="Preferências de notificação por usuário",
    )

    op.create_table(
        "tb_despesa_destinatarios",
        sa.Column("despesa_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("despesa_id", "user_id"),
        sa.ForeignKeyConstraint(
            ["despesa_id"],
            ["tb_despesas.id"],
            name="fk_destinatario_despesa",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["tb_users.id"],
            name="fk_destinatario_user",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        comment="Quais usuários devem ser notificados de cada despesa",
    )
    op.create_index(
        "ix_tb_despesa_destinatarios_user_id",
        "tb_despesa_destinatarios",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_tb_despesa_destinatarios_user_id",
        table_name="tb_despesa_destinatarios",
    )
    op.drop_table("tb_despesa_destinatarios")
    op.drop_table("tb_notificacao_config")
