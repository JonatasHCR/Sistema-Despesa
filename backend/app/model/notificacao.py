from sqlalchemy import (
    Boolean,
    Column,
    ForeignKeyConstraint,
    Index,
    Integer,
    PrimaryKeyConstraint,
)

from app.core.database import Base


class NotificacaoConfig(Base):
    __tablename__ = "tb_notificacao_config"
    __comment__ = "Preferências de notificação por usuário"

    user_id = Column(Integer, primary_key=True)
    ativo = Column(Boolean, nullable=False, default=True)
    dias_antecedencia = Column(Integer, nullable=False, default=5)
    avisar_vencidas = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["tb_users.id"],
            name="fk_notif_config_user",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )


class DespesaDestinatario(Base):
    __tablename__ = "tb_despesa_destinatarios"
    __comment__ = "Quais usuários devem ser notificados de cada despesa"

    despesa_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("despesa_id", "user_id"),
        ForeignKeyConstraint(
            ["despesa_id"],
            ["tb_despesas.id"],
            name="fk_destinatario_despesa",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["tb_users.id"],
            name="fk_destinatario_user",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        Index("ix_tb_despesa_destinatarios_user_id", "user_id"),
    )
