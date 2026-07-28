from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class MudancaAplicacaoValidator(AbstractDespesaValidator):
    """REG-013 — Validações de mudança de tipo de aplicação (CAPITAL ↔ CUSTEIO) em rateios existentes.
    R21 — Reset de campos incompatíveis ao mudar CAPITAL ↔ CUSTEIO (fase apply).

    Presente apenas em UPDATE_PIPELINE e UPDATE_ACERTO_PIPELINE (pipelines.py).

    Legado: despesa_service.py:234-355 (_atualizar_rateios)
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — verifica se a mudança de aplicação (CAPITAL↔CUSTEIO) em rateios existentes é válida.

        Ignorado quando ctx.despesa_instance é None (criação não usa este validator).
        Levanta DespesaValidationError com detail={"mensagem": "..."} no primeiro rateio com violação.
        """
        if ctx.despesa_instance:
            self._validar_mudancas_de_aplicacao(ctx.rateios, ctx.despesa_instance)
        return ctx

    def apply(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """R21 — Reseta campos incompatíveis quando a aplicação do rateio muda.

        Legado: despesa_service.py:300-313 (CAPITAL→CUSTEIO) e 343-350 (CUSTEIO→CAPITAL)
        """
        if ctx.despesa_instance:
            self._resetar_campos_por_mudanca(ctx.rateios, ctx.despesa_instance)
        return ctx

    def _validar_mudancas_de_aplicacao(self, rateios: list, despesa) -> None:
        for rateio in rateios:
            # despesa_service.py:257
            if "uuid" not in rateio:
                continue

            # despesa_service.py:262-265
            rateio_atual = RateioDespesa.objects.filter(uuid=rateio["uuid"]).first()
            if not rateio_atual:
                continue

            # despesa_service.py:267-276
            aplicacao_anterior = rateio_atual.aplicacao_recurso
            nova_aplicacao = rateio.get("aplicacao_recurso")
            sem_exigencia = self._sem_exigencia_especificacao(rateio, rateio_atual, despesa)

            # despesa_service.py:279-318
            if aplicacao_anterior == APLICACAO_CAPITAL and nova_aplicacao == APLICACAO_CUSTEIO:
                self._validar_capital_para_custeio(rateio, sem_exigencia)

            # despesa_service.py:320-354
            elif aplicacao_anterior == APLICACAO_CUSTEIO and nova_aplicacao == APLICACAO_CAPITAL:
                self._validar_custeio_para_capital(rateio, rateio_atual, sem_exigencia)

    def _resetar_campos_por_mudanca(self, rateios: list, despesa) -> None:
        for rateio in rateios:
            if "uuid" not in rateio:
                continue

            rateio_atual = RateioDespesa.objects.filter(uuid=rateio["uuid"]).first()
            if not rateio_atual:
                continue

            aplicacao_anterior = rateio_atual.aplicacao_recurso
            nova_aplicacao = rateio.get("aplicacao_recurso")

            if aplicacao_anterior == nova_aplicacao:
                continue

            sem_exigencia = self._sem_exigencia_especificacao(rateio, rateio_atual, despesa)

            # despesa_service.py:300-313
            if aplicacao_anterior == APLICACAO_CAPITAL and nova_aplicacao == APLICACAO_CUSTEIO:
                self._resetar_campos_capital(rateio, sem_exigencia)
            # despesa_service.py:343-350
            elif aplicacao_anterior == APLICACAO_CUSTEIO and nova_aplicacao == APLICACAO_CAPITAL:
                self._resetar_campos_custeio(rateio, sem_exigencia)

    @staticmethod
    def _sem_exigencia_especificacao(rateio, rateio_atual, despesa) -> bool:
        """despesa_service.py:271-276."""
        saida_recurso_externo = rateio.get(
            "saida_de_recurso_externo",
            rateio_atual.saida_de_recurso_externo,
        )
        return despesa.eh_despesa_sem_comprovacao_fiscal or saida_recurso_externo

    @staticmethod
    def _validar_capital_para_custeio(rateio: dict, sem_exigencia: bool) -> None:
        """R17, R18 — despesa_service.py:279-318."""
        if sem_exigencia:
            return

        tipo_custeio = rateio.get("tipo_custeio")
        especificacao = rateio.get("especificacao_material_servico")

        # despesa_service.py:284-291
        if not tipo_custeio or not especificacao:
            raise DespesaValidationError({
                "mensagem": (
                    "Ao alterar o tipo de aplicação de Capital para Custeio, "
                    "é obrigatório informar o Tipo de Custeio e a Especificação de "
                    "Material ou Serviço em cada rateio."
                ),
                "validator": "MudancaAplicacaoValidator"
            })

        # despesa_service.py:292-299
        if especificacao.aplicacao_recurso != APLICACAO_CUSTEIO:
            raise DespesaValidationError({
                "mensagem": (
                    "Ao alterar o tipo de aplicação de Capital para Custeio, "
                    "é obrigatório informar uma Especificação de Material ou Serviço "
                    "de Custeio. A especificação atual é de Capital."
                ),
                "validator": "MudancaAplicacaoValidator"
            })

    @staticmethod
    def _validar_custeio_para_capital(rateio: dict, rateio_atual, sem_exigencia: bool) -> None:
        """R19, R20 — despesa_service.py:320-354."""
        if sem_exigencia:
            return

        # despesa_service.py:323-326
        especificacao = rateio.get("especificacao_material_servico")
        if especificacao is None:
            especificacao = rateio_atual.especificacao_material_servico

        # despesa_service.py:326-333
        if not especificacao:
            raise DespesaValidationError({
                "mensagem": (
                    "Ao alterar o tipo de aplicação de Custeio para Capital, "
                    "é obrigatório informar a Especificação de Material ou Serviço "
                    "de Capital em cada rateio."
                ),
                "validator": "MudancaAplicacaoValidator"
            })

        # despesa_service.py:334-341
        if especificacao.aplicacao_recurso != APLICACAO_CAPITAL:
            raise DespesaValidationError({
                "mensagem": (
                    "Ao alterar o tipo de aplicação de Custeio para Capital, "
                    "é obrigatório informar uma Especificação de Material ou Serviço "
                    "de Capital. A especificação atual é de Custeio."
                ),
                "validator": "MudancaAplicacaoValidator"
            })

    @staticmethod
    def _resetar_campos_capital(rateio: dict, sem_exigencia: bool) -> None:
        """R21 — Limpa campos de CAPITAL ao migrar para CUSTEIO. despesa_service.py:300-313."""
        updates = {
            "numero_processo_incorporacao_capital": "",
            "quantidade_itens_capital": 0,
            "nao_exibir_em_rel_bens": False,
            "valor_item_capital": 0,
        }
        if sem_exigencia:
            updates["especificacao_material_servico"] = None
        rateio.update(updates)

    @staticmethod
    def _resetar_campos_custeio(rateio: dict, sem_exigencia: bool) -> None:
        """R21 — Limpa campos de CUSTEIO ao migrar para CAPITAL. despesa_service.py:343-350."""
        updates = {"tipo_custeio": None}
        if sem_exigencia:
            updates["especificacao_material_servico"] = None
        rateio.update(updates)
