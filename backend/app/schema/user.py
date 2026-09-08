
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class UserSchema(BaseModel):
    """Criação de usuário. Sem senha: quem guarda credencial é o Keycloak.

    Continua existindo para o cadastro feito por quem já está autenticado; o
    caminho normal, porém, é o provisionamento automático no primeiro login.
    """

    nome: str = Field(..., description="Nome do usuário")
    email: EmailStr = Field(..., description="Email do usuário")

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(BaseModel):
    nome: Optional[str] = Field(None, description="Nome do usuário")
    email: Optional[EmailStr] = Field(None, description="Email do usuário")

    model_config = ConfigDict(from_attributes=True, exclude_none=True)


class UserOutputSchema(BaseModel):
    id: int = Field(..., gt=0)
    nome: str = Field(..., description="Nome do usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    # Exposto para o front decidir se mostra o link de Administração. Esconder
    # o link é conveniência: quem barra de verdade é o `get_current_admin` em
    # cada rota de /manutencao.
    admin: bool = Field(False, description="Pode abrir a tela de Administração")

    model_config = ConfigDict(from_attributes=True)
