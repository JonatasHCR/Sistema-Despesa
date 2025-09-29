from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict, field_validator


class DespesaSchema(BaseModel):

    nome: str = Field(..., description="Nome da despesa")
    tipo: str = Field(..., description="Tipo da despesa")
    status: Literal["P", "Q"] = Field(
        ..., description="Status da despesa: P - Pendente, Q - Quitada"
    )
    vencimento: date = Field(..., description="Data de vencimento da despesa")
    valor: float = Field(..., gt=0, description="Valor da despesa")
    user_id: int = Field(..., gt=0, description="Usuário que está relacionado")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @field_validator("vencimento", mode="before")
    @classmethod
    def format_date(cls, value):
        if isinstance(value, str):
            return date.fromisoformat(value.split("T")[0])
        return value


class DespesaOutputSchema(DespesaSchema):
    id: int = Field(..., gt=0)
