"""user.nome unique + desambiguação de duplicados

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-19 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # Renomeia duplicados antes de criar o índice único: "joao" duplicado vira "joao", "joao (2)", "joao (3)"...
    rows = bind.execute(sa.text("SELECT id, nome FROM tb_users ORDER BY id")).fetchall()
    seen: dict[str, int] = {}
    for user_id, nome in rows:
        if nome is None:
            continue
        count = seen.get(nome, 0) + 1
        seen[nome] = count
        if count > 1:
            new_nome = f"{nome} ({count})"
            # Garante que o novo nome também não colide
            while bind.execute(
                sa.text("SELECT 1 FROM tb_users WHERE nome = :n AND id <> :i"),
                {"n": new_nome, "i": user_id},
            ).first():
                count += 1
                new_nome = f"{nome} ({count})"
            bind.execute(
                sa.text("UPDATE tb_users SET nome = :n WHERE id = :i"),
                {"n": new_nome, "i": user_id},
            )

    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_tb_users_nome'
                  AND conrelid = 'tb_users'::regclass
            ) THEN
                ALTER TABLE tb_users ADD CONSTRAINT uq_tb_users_nome UNIQUE (nome);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.drop_constraint("uq_tb_users_nome", "tb_users", type_="unique")
