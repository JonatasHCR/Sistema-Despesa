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
    tipo = Column(String(100), nullable=False)
    valor = Column(Numeric, nullable=False)
    status = Column(String(1), nullable=False)
    vencimento = Column(Date, nullable=False, comment="Data de vencimento da despesa")
    descricao = Column(String(20), nullable=True, default="PARCELA ÚNICA", comment="Descrição da despesa, ex: 'Parcela 1 de 3'")
    user_id = Column(
        Integer, nullable=False, comment="ID do usuário que criou a despesa"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('P', 'Q')",
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
