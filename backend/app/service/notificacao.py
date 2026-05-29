from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.despesa import DespesaRepository
from app.repository.notificacao import NotificacaoConfigRepository
from app.schema.notificacao import (
    DigestItemSchema,
    DigestSchema,
    NotificacaoConfigSchema,
    NotificacaoConfigUpdateSchema,
)


_DEFAULTS = {"ativo": True, "dias_antecedencia": 5, "avisar_vencidas": True}


class NotificacaoService:
    def __init__(self, db: AsyncSession):
        self.repo = NotificacaoConfigRepository(db)
        self.despesa_repo = DespesaRepository(db)

    async def get_config(self, user_id: int) -> NotificacaoConfigSchema:
        config = await self.repo.get_by_user(user_id)
        if config is None:
            config = await self.repo.create(user_id=user_id, **_DEFAULTS)
        return NotificacaoConfigSchema.model_validate(config)

    async def update_config(
        self, user_id: int, schema: NotificacaoConfigUpdateSchema
    ) -> NotificacaoConfigSchema:
        mudancas = schema.model_dump(exclude_none=True)
        config = await self.repo.get_by_user(user_id)
        if config is None:
            config = await self.repo.create(
                user_id=user_id, **{**_DEFAULTS, **mudancas}
            )
        else:
            config = await self.repo.update_by_user(user_id, **mudancas)
        return NotificacaoConfigSchema.model_validate(config)

    async def get_digest(self, user_id: int) -> DigestSchema:
        config = await self.repo.get_by_user(user_id)
        ativo = _DEFAULTS["ativo"] if config is None else config.ativo
        dias = _DEFAULTS["dias_antecedencia"] if config is None else config.dias_antecedencia
        avisar_vencidas = (
            _DEFAULTS["avisar_vencidas"] if config is None else config.avisar_vencidas
        )
        hoje = date.today()

        if not ativo:
            return DigestSchema(data=hoje, total=0, vencidas=0, vencendo=0, itens=[])

        limite = hoje + timedelta(days=dias)
        despesas = await self.despesa_repo.get_pendentes_para_usuario(user_id, limite)

        itens: list[DigestItemSchema] = []
        vencidas = 0
        vencendo = 0
        for despesa in despesas:
            diff = (despesa.vencimento - hoje).days
            if diff < 0:
                if not avisar_vencidas:
                    continue
                situacao = "vencida"
                vencidas += 1
            else:
                situacao = "vencendo"
                vencendo += 1
            itens.append(
                DigestItemSchema(
                    id=despesa.id,
                    nome=despesa.nome,
                    tipo=despesa.tipo,
                    valor=float(despesa.valor),
                    vencimento=despesa.vencimento,
                    descricao=despesa.descricao,
                    situacao=situacao,
                    dias=diff,
                )
            )

        return DigestSchema(
            data=hoje,
            total=len(itens),
            vencidas=vencidas,
            vencendo=vencendo,
            itens=itens,
        )
