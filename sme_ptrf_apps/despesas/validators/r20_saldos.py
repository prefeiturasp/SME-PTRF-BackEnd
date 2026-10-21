from .base import AbstractDespesaValidator
from .context import DespesaDtoContext


class SaldosValidator(AbstractDespesaValidator):
    """REG-020 — Verifica saldo disponível em contas e ações para cobrir os rateios.

    Utiliza rateios_raw (UUID strings) pois valida_rateios_quanto_aos_saldos e
    saldos_insuficientes_para_rateios esperam conta_associacao/acao_associacao como UUIDs.

    Legado: sem equivalente direto no serializer/service — chamado externamente via viewset.
    o frontend verifica o saldo em rateios-despesas/verificar-saldos/ pelo service:
    - .../SME-PTRF-FrontEnd/src/services/escolas/RateiosDespesas.service.js
    aciona viewset sme_ptrf_apps/despesas/api/views/rateios_despesas_viewset.py::verificar_saldos
    e realiza uma verificacao se aceitar_lancamento=True

    Mas esta regra pode não ser considerada uma validação de criação/edição de despesa, pois não impede a
    criação/edição da despesa se houver uma interação de confirmação no frontend, logo, não pode ser um impeditivo.

    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — verifica saldo disponível em contas/ações para cobrir os rateios.

        Desativado: esta regra não é impeditiva de criação/edição —
        o frontend exibe confirmação e o usuário pode aceitar lançamento mesmo sem saldo.
        Ver docstring da classe para referência do fluxo legado.
        """
        # considerar_na_pipeline = False
        # if not considerar_na_pipeline:
        #     return ctx
        #
        # from sme_ptrf_apps.core.services import valida_rateios_quanto_aos_saldos
        # from .base import DespesaValidationError
        #
        # if not ctx.data_transacao or not ctx.associacao:
        #     return ctx
        #
        # recurso = ctx.recurso_efetivo
        # exclude_uuid = str(ctx.despesa_instance.uuid) if ctx.despesa_instance else None
        # rateios_formatados = self._garantir_uuids(ctx.rateios_raw)
        # result = valida_rateios_quanto_aos_saldos(
        #     rateios=rateios_formatados,
        #     associacao=ctx.associacao,
        #     data_documento=ctx.data_transacao,
        #     exclude_despesa=exclude_uuid,
        #     recurso=recurso,
        # )
        # ctx.saldos = result
        # if not result.get("aceitar_lancamento", True):
        #     raise DespesaValidationError(result)

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
