"""hash existing plaintext passwords + add indexes

Revision ID: a1b2c3d4e5f6
Revises: 6f4042640b7f
Create Date: 2026-05-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import bcrypt


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "6f4042640b7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_BCRYPT_PREFIXES = ("$2a$", "$2b$", "$2y$")


def upgrade() -> None:
    bind = op.get_bind()
    users = bind.execute(sa.text("SELECT id, senha FROM tb_users")).fetchall()
    for user_id, senha in users:
        if not senha or senha.startswith(_BCRYPT_PREFIXES):
            continue
        hashed = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        bind.execute(
            sa.text("UPDATE tb_users SET senha = :hashed WHERE id = :id"),
            {"hashed": hashed, "id": user_id},
        )

    op.create_index("ix_tb_despesas_user_id", "tb_despesas", ["user_id"])
    op.create_index("ix_tb_users_nome", "tb_users", ["nome"])


def downgrade() -> None:
    op.drop_index("ix_tb_users_nome", table_name="tb_users")
    op.drop_index("ix_tb_despesas_user_id", table_name="tb_despesas")
    # Não é possível desfazer o hash de senhas; intencional.
