"""initial schema (tb_users + tb_despesas)

Idempotente: usa CREATE TABLE IF NOT EXISTS para que rodar em um banco que já
tinha as tabelas (criadas pelo antigo Base.metadata.create_all do lifespan)
seja no-op.

Revision ID: 0000000000
Revises:
Create Date: 2026-05-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "0000000000"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS tb_users (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(255),
            senha TEXT NOT NULL
        );
        """
    )
    # email único quando presente (NULL pode repetir até a migration que torna NOT NULL)
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_tb_users_email ON tb_users (email);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_tb_users_id ON tb_users (id);")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS tb_despesas (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            tipo VARCHAR(100) NOT NULL,
            valor NUMERIC NOT NULL,
            status VARCHAR(1) NOT NULL,
            vencimento DATE NOT NULL,
            user_id INTEGER NOT NULL,
            CONSTRAINT ck_despesas_tipo CHECK (status IN ('P', 'Q')),
            CONSTRAINT fk_despesa_user_id FOREIGN KEY (user_id)
                REFERENCES tb_users (id) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_tb_despesas_id ON tb_despesas (id);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS tb_despesas;")
    op.execute("DROP TABLE IF EXISTS tb_users;")
