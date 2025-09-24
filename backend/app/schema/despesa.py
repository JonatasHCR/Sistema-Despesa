from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field, ConfigDict


class DespesaSchema(BaseModel):

    nome: str = Field(..., description="Nome da despesa")
    tipo: Optional[Literal["N", "B"]]
    vencimento: date = Field(..., description="Data de vencimento do ativo")
    valor: float = Field(..., gt=0, description="Valor da despesa")
    user_id: int = Field(..., gt=0, description="Usuário que está relacionado")

    model_config = ConfigDict(from_attributes=True)


class DespesaOutputSchema(DespesaSchema):
    id: int = Field(..., gt=0)
