from pydantic import BaseModel, Field, ConfigDict, EmailStr


class UserSchema(BaseModel):

    nome: str = Field(..., description="Nome do ativo")
    email: EmailStr = Field(..., description="Email do usuário")
    senha: str = Field(..., min_length=6, description="Senha do usuário")

    model_config = ConfigDict(from_attributes=True)


class UserOutputSchema(UserSchema):
    id: int = Field(..., gt=0)
