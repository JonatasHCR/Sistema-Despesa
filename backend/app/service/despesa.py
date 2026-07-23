from sqlalchemy.ext.asyncio import AsyncSession

from app.schema.despesa import (
    DespesaOutputSchema,
    DespesaSchema,
    DespesaUpdateSchema,
    ImportResultSchema,
)
from app.repository.despesa import DespesaRepository
from app.service.excel_import import parse_despesas_xlsx
from .base import BaseService


class DespesaService(
    BaseService[DespesaRepository, DespesaSchema, DespesaUpdateSchema, DespesaOutputSchema]
):
    def __init__(self, db: AsyncSession):
        super().__init__(DespesaRepository, DespesaOutputSchema, db)

    async def _resolver_destinatarios(
        self, destinatarios: list[int] | None, owner_id: int
    ) -> list[int]:
        """None -> notifica o dono; lista -> usa só os user_ids que existem (sem duplicar)."""
        candidatos = [owner_id] if destinatarios is None else destinatarios
        validos = await self.repository.existing_user_ids(candidatos)
        return [uid for uid in dict.fromkeys(candidatos) if uid in validos]

    async def update_partial(self, id: int, schema: DespesaUpdateSchema) -> DespesaOutputSchema:
        data = schema.model_dump(exclude_unset=True, exclude_none=True)
        destinatarios = data.pop("destinatarios", None)

        if data:
            despesa = await self.repository.update(id, **data)
        else:
            despesa = await self.repository.get_by_id(id)

        if destinatarios is not None:
            dest_ids = await self._resolver_destinatarios(
                destinatarios, owner_id=despesa.user_id
            )
            await self.repository.set_destinatarios(id, dest_ids)

        despesa.destinatarios = await self.repository.get_destinatarios(id)
        return DespesaOutputSchema.model_validate(despesa)

    async def get_one(self, id: int) -> DespesaOutputSchema:
        despesa = await self.repository.get_by_id(id)
        despesa.destinatarios = await self.repository.get_destinatarios(id)
        return DespesaOutputSchema.model_validate(despesa)

    async def get_by_user_id(self, user_id: int) -> list[DespesaOutputSchema]:
        busca = await self.repository.get_by_user_id(user_id)
        return [DespesaOutputSchema.model_validate(objeto) for objeto in busca]

    async def list_with_user(self, limit: int = 100, offset: int = 0) -> list[DespesaOutputSchema]:
        rows = await self.repository.list_with_user(limit=limit, offset=offset)
        return [
            DespesaOutputSchema.model_validate({
                **{c.name: getattr(despesa, c.name) for c in despesa.__table__.columns},
                "user_nome": user_nome,
            })
            for despesa, user_nome in rows
        ]

    async def create_for_user(self, schema: DespesaSchema, user_id: int) -> DespesaOutputSchema:
        data = schema.model_dump()
        destinatarios = data.pop("destinatarios", None)
        data["user_id"] = user_id

        despesa = await self.repository.create(**data)
        dest_ids = await self._resolver_destinatarios(destinatarios, owner_id=user_id)
        await self.repository.set_destinatarios(despesa.id, dest_ids)

        despesa.destinatarios = dest_ids
        return DespesaOutputSchema.model_validate(despesa)

    async def create_many_for_user(self, schemas: list[DespesaSchema], user_id: int) -> int:
        if not schemas:
            return 0
        rows = []
        for schema in schemas:
            data = schema.model_dump() | {"user_id": user_id}
            data.pop("destinatarios", None)  # não é coluna de tb_despesas
            rows.append(data)
        criadas = await self.repository.create_many(rows)
        # Importadas notificam o dono por padrão.
        await self.repository.add_destinatarios_bulk(
            [{"despesa_id": d.id, "user_id": user_id} for d in criadas]
        )
        return len(criadas)

    async def import_excel(self, content: bytes, user_id: int) -> ImportResultSchema:
        """Lê um .xlsx, cria as linhas válidas e reporta as inválidas."""
        validos, erros, total = parse_despesas_xlsx(content)
        criadas = await self.create_many_for_user(validos, user_id)
        return ImportResultSchema(
            total_linhas=total,
            criadas=criadas,
            falhas=len(erros),
            erros=erros,
        )
