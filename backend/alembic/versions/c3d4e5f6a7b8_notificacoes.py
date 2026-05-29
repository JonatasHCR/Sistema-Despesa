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
    op.execute("""
        CREATE TABLE IF NOT EXISTS tb_notificacao_config (
            user_id INTEGER NOT NULL,
            ativo BOOLEAN NOT NULL DEFAULT true,
            dias_antecedencia INTEGER NOT NULL DEFAULT 5,
            avisar_vencidas BOOLEAN NOT NULL DEFAULT true,
            PRIMARY KEY (user_id),
            CONSTRAINT fk_notif_config_user FOREIGN KEY (user_id)
                REFERENCES tb_users (id) ON DELETE CASCADE ON UPDATE CASCADE
        );
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS tb_despesa_destinatarios (
            despesa_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY (despesa_id, user_id),
            CONSTRAINT fk_destinatario_despesa FOREIGN KEY (despesa_id)
                REFERENCES tb_despesas (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fk_destinatario_user FOREIGN KEY (user_id)
                REFERENCES tb_users (id) ON DELETE CASCADE ON UPDATE CASCADE
        );
    """)

    op.create_index(
        "ix_tb_despesa_destinatarios_user_id",
        "tb_despesa_destinatarios",
        ["user_id"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_tb_despesa_destinatarios_user_id",
        table_name="tb_despesa_destinatarios",
    )
    op.drop_table("tb_despesa_destinatarios")
    op.drop_table("tb_notificacao_config")
