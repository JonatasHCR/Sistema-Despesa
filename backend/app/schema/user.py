from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class UserSchema(BaseModel):

    nome: str = Field(..., description="Nome do ativo")
    email: EmailStr = Field(..., description="Email do usuário")
    senha: str = Field(None, min_length=6, description="Senha do usuário")

    model_config = ConfigDict(from_attributes=True)


class UserOutputSchema(BaseModel):
    id: int = Field(..., gt=0)
    nome: str = Field(..., description="Nome do ativo")
    senha: str = Field(..., min_length=6, description="Senha do usuário")
    email: EmailStr = Field(..., description="Email do usuário")

    model_config = ConfigDict(from_attributes=True)
