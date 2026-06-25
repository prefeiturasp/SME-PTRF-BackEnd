from sme_ptrf_apps.core.services import valida_rateios_quanto_aos_saldos

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class SaldosValidator(AbstractDespesaValidator):
    """R42-R45 — Verifica saldo disponível em contas e ações para cobrir os rateios.

    Utiliza `rateios_raw` (UUID strings) pois `valida_rateios_quanto_aos_saldos` e
    `saldos_insuficientes_para_rateios` esperam conta_associacao/acao_associacao como UUIDs.

    Quando aceitar_lancamento=False, o lançamento é bloqueado. Caso contrário, o resultado
    é armazenado em ctx.saldos para uso posterior (ex: resposta ao frontend).
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        if not ctx.data_transacao or not ctx.associacao:
            return ctx

        recurso = ctx.recurso_efetivo
        exclude_uuid = str(ctx.despesa_instance.uuid) if ctx.despesa_instance else None

        rateios_formatados = self._garantir_uuids(ctx.rateios_raw)

        result = valida_rateios_quanto_aos_saldos(
            rateios=rateios_formatados,
            associacao=ctx.associacao,
            data_documento=ctx.data_transacao,
            exclude_despesa=exclude_uuid,
            recurso=recurso,
        )

        ctx.saldos = result

        if not result.get("aceitar_lancamento", True):
            raise DespesaValidationError(result)

        return ctx

    @staticmethod
    def _garantir_uuids(rateios: list) -> list:
        """Converte instâncias de model para UUID string, caso necessário."""
        adapted = []
        for r in rateios:
            item = dict(r)
            for campo in ("conta_associacao", "acao_associacao"):
                val = item.get(campo)
                if val and hasattr(val, "uuid"):
                    item[campo] = str(val.uuid)
            adapted.append(item)
        return adapted
