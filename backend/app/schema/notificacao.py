from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class NotificacaoConfigSchema(BaseModel):
    ativo: bool = True
    dias_antecedencia: int = Field(
        5, ge=0, le=365, description="Avisar despesas vencendo em até N dias"
    )
    avisar_vencidas: bool = True

    model_config = ConfigDict(from_attributes=True)


class NotificacaoConfigUpdateSchema(BaseModel):
    ativo: Optional[bool] = None
    dias_antecedencia: Optional[int] = Field(None, ge=0, le=365)
    avisar_vencidas: Optional[bool] = None


class DigestItemSchema(BaseModel):
    id: int
    nome: str
    tipo: str
    valor: float
    vencimento: date
    descricao: Optional[str] = None
    situacao: Literal["vencida", "vencendo"]
    dias: int = Field(
        ..., description="Dias até o vencimento (negativo = vencida há N dias)"
    )

    model_config = ConfigDict(from_attributes=True)


class DigestSchema(BaseModel):
    data: date
    total: int
    vencidas: int
    vencendo: int
    itens: list[DigestItemSchema]
