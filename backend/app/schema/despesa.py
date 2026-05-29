from datetime import date
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator

from app.core.enums import DespesaStatusEnum


class DespesaBase(BaseModel):
    nome: str = Field(..., description="Nome da despesa")
    tipo: str = Field(..., description="Tipo da despesa")
    status: DespesaStatusEnum = Field(
        ..., description="Status da despesa: P - Pendente, Q - Quitada"
    )
    vencimento: date = Field(..., description="Data de vencimento da despesa")
    valor: float = Field(..., gt=0, description="Valor da despesa")
    descricao: Optional[str] = Field("PARCELA ÚNICA", max_length=20, description="Descrição da despesa")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, use_enum_values=True)

    @field_validator("vencimento", mode="before")
    @classmethod
    def format_date(cls, value):
        if isinstance(value, str):
            return date.fromisoformat(value.split("T")[0])
        return value


class DespesaSchema(DespesaBase):
    """Schema de entrada — o user_id é injetado pelo endpoint a partir do token."""

    destinatarios: Optional[list[int]] = Field(
        None,
        description="IDs dos usuários a notificar. None = notifica o dono; lista vazia = ninguém.",
    )


class DespesaUpdateSchema(BaseModel):
    """Update parcial — todos os campos opcionais. Backend funde com o estado atual."""

    nome: Optional[str] = None
    tipo: Optional[str] = None
    status: Optional[Literal["P", "Q"]] = None
    vencimento: Optional[date] = None
    valor: Optional[float] = Field(None, gt=0)
    descricao: Optional[str] = Field(None, max_length=20)
    destinatarios: Optional[list[int]] = Field(
        None, description="Se enviado, substitui a lista de destinatários da despesa."
    )

    model_config = ConfigDict(from_attributes=True)

    @field_validator("vencimento", mode="before")
    @classmethod
    def format_date(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            return date.fromisoformat(value.split("T")[0])
        return value


class DespesaOutputSchema(DespesaBase):
    id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    user_nome: Optional[str] = Field(None, description="Nome do usuário (join)")
    destinatarios: list[int] = Field(
        default_factory=list, description="IDs dos usuários notificados desta despesa"
    )

    @model_validator(mode="before")
    @classmethod
    def _from_orm(cls, data: Any):
        # Permite passar um ORM Despesa direto (sem o join) — user_nome fica None.
        if hasattr(data, "__table__"):
            base = {c.name: getattr(data, c.name) for c in data.__table__.columns}
            base["user_nome"] = getattr(data, "user_nome", None)
            base["destinatarios"] = getattr(data, "destinatarios", []) or []
            return base
        return data


class ImportRowError(BaseModel):
    linha: int = Field(..., description="Número da linha na planilha (1 = cabeçalho)")
    erro: str = Field(..., description="Motivo pelo qual a linha foi rejeitada")


class ImportResultSchema(BaseModel):
    total_linhas: int = Field(..., description="Total de linhas de dados lidas")
    criadas: int = Field(..., description="Quantas despesas foram criadas")
    falhas: int = Field(..., description="Quantas linhas foram rejeitadas")
    erros: list[ImportRowError] = Field(default_factory=list)
