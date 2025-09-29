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
from app.core.enums import DespesaStatusEnum


class Despesa(Base):
    __tablename__ = "tb_despesas"
    __comment__ = "Tabela de despesas do sistema"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(100), nullable=False)
    valor = Column(Numeric, nullable=False)
    status = Column(String(1), nullable=False)
    vencimento = Column(Date, nullable=False, comment="Data de vencimento da despesa")
    user_id = Column(
        Integer, nullable=False, comment="ID do usuário que criou a despesa"
    )

    __table_args__ = (
        CheckConstraint(
            status.in_([s.value for s in DespesaStatusEnum]),
            name="ck_despesas_status",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["tb_users.id"],
            name="fk_despesa_user_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )
