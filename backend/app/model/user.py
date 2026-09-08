from sqlalchemy import (
    Boolean,
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

    # Nulo desde que a autenticação passou ao Keycloak. A coluna continua
    # existindo para não quebrar linhas antigas, mas nada mais a lê nem a
    # escreve — nenhum hash legado foi migrado, o reset foi forçado.
    senha = Column(Text, nullable=True)

    # O `sub` do Keycloak (UUID). É o vínculo estável entre a conta local e a
    # identidade: no primeiro login o usuário é achado por email e este campo é
    # gravado; daí em diante o casamento é por aqui. Nulo para quem ainda não
    # entrou uma vez pelo SSO.
    external_id = Column(String(64), nullable=True, unique=True, index=True)

    # Espelha o acesso concedido no Keycloak.
    #
    # Vira False quando a pessoa perde o grupo `/apps/despesa` — a conta NÃO é
    # apagada, porque há despesas, destinatários e configurações de notificação
    # apontando para ela, e porque o histórico precisa continuar legível. Volta
    # a True se o acesso for devolvido.
    #
    # Serve para duas coisas: deixar visível aqui dentro quem perdeu o acesso, e
    # barrar a pessoa mesmo que ela chegue com um token ainda válido.
    ativo = Column(Boolean, nullable=False, server_default='true', default=True)

    # Único papel que este sistema conhece, e existe por um motivo estreito: a
    # tela de Administração (backup, limpeza, restauração) precisa de um dono.
    #
    # NÃO governa despesas. O sistema é usado por pessoas do mesmo setor e
    # qualquer um autenticado edita a despesa de outro — isso continua igual.
    # Confundir os dois seria transformar uma ferramenta de infraestrutura em
    # hierarquia de negócio.
    admin = Column(Boolean, nullable=False, server_default='false', default=False)
