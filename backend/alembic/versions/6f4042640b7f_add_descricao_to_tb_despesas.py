"""add descricao to tb_despesas

Revision ID: 6f4042640b7f
Revises: 
Create Date: 2026-04-06 14:34:05.045011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f4042640b7f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        ALTER TABLE tb_despesas
        ADD COLUMN IF NOT EXISTS descricao VARCHAR(20) DEFAULT 'PARCELA ÚNICA';
    """)


def downgrade():
    op.execute("""
        ALTER TABLE tb_despesas
        DROP COLUMN IF EXISTS descricao;
    """)