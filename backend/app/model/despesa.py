from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Date,
    CheckConstraint,
    ForeignKeyConstraint,
)
from app.core.database import Base


class Despesa(Base):
    __tablename__ = "tb_despesas"
    __comment__ = "Tabela de despesas do sistema"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(1), nullable=False)
    valor = Column(Numeric, nullable=False)
    vencimento = Column(Date, nullable=False, comment="Data de vencimento da despesa")
    user_id = Column(
        Integer, nullable=False, comment="ID do usuário que criou a despesa"
    )

    __table_args__ = (
        CheckConstraint(
            "tipo IN ('B', 'N')",
            "ck_despesas_tipo",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["tb_users.id"],
            name="fk_despesa_user_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )
