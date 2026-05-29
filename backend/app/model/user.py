from sqlalchemy import (
    Column,
    Integer,
    String,
    Text
)
from app.core.database import Base


class User(Base):
    __tablename__ = "tb_users"
    __comment__ = "Tabela de usuários do sistema"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True)
    senha = Column(Text, nullable=False)
