from datetime import date
from app.core.enums import DespesaStatusEnum
from pydantic import BaseModel, Field, ConfigDict, field_validator


class DespesaSchema(BaseModel):

    nome: str = Field(..., description="Nome da despesa")
    tipo: str = Field(..., description="Tipo da despesa")
    status: DespesaStatusEnum = Field(
        ..., description="Status da despesa: P - Pendente, Q - Quitada"
    )
    vencimento: date = Field(..., description="Data de vencimento da despesa")
    valor: float = Field(..., gt=0, description="Valor da despesa")
    user_id: int = Field(..., gt=0, description="Usuário que está relacionado")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, use_enum_values=True)

    @field_validator("vencimento", mode="before")
    @classmethod
    def format_date(cls, value):
        if isinstance(value, str):
            return date.fromisoformat(value.split("T")[0])
        return value


class DespesaOutputSchema(DespesaSchema):
    id: int = Field(..., gt=0)
