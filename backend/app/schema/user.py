
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class UserSchema(BaseModel):

    nome: str = Field(..., description="Nome do usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    senha: str = Field(..., min_length=3, description="Senha do usuário")

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(BaseModel):
    nome: Optional[str] = Field(None, description="Nome do usuário")
    email: Optional[EmailStr] = Field(None, description="Email do usuário")
    senha: Optional[str] = Field(None, min_length=3, description="Nova senha do usuário")

    model_config = ConfigDict(from_attributes=True, exclude_none=True)


class UserOutputSchema(BaseModel):
    id: int = Field(..., gt=0)
    nome: str = Field(..., description="Nome do usuário")
    senha: str = Field(..., min_length=3, description="Senha do usuário")
    email: EmailStr = Field(..., description="Email do usuário")

    model_config = ConfigDict(from_attributes=True)
