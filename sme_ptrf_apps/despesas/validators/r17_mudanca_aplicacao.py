from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class MudancaAplicacaoValidator(AbstractDespesaValidator):
    """R17-R20 — Validações de mudança de tipo de aplicação (CAPITAL ↔ CUSTEIO) em rateios existentes.
    R21 — Reset de campos incompatíveis ao mudar CAPITAL ↔ CUSTEIO (fase apply).

    Migrado de DespesaService._atualizar_rateios() para separar validação (fase 1)
    de mutação (fase 2).

    Só se aplica no update. No create, todos os rateios são novos e a aplicação não muda.
    """

    applies_to_create = False

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        if not ctx.despesa_instance:
            return ctx

        despesa = ctx.despesa_instance

        for rateio in ctx.rateios:
            if "uuid" not in rateio:
                continue

            rateio_atual = RateioDespesa.objects.filter(uuid=rateio["uuid"]).first()
            if not rateio_atual:
                continue

            aplicacao_anterior = rateio_atual.aplicacao_recurso
            nova_aplicacao = rateio.get("aplicacao_recurso")

            saida_recurso_externo = rateio.get(
                "saida_de_recurso_externo",
                rateio_atual.saida_de_recurso_externo,
            )
            sem_exigencia_especificacao = (
                despesa.eh_despesa_sem_comprovacao_fiscal or saida_recurso_externo
            )

            if aplicacao_anterior == APLICACAO_CAPITAL and nova_aplicacao == APLICACAO_CUSTEIO:
                self._validar_capital_para_custeio(rateio, sem_exigencia_especificacao)

            elif aplicacao_anterior == APLICACAO_CUSTEIO and nova_aplicacao == APLICACAO_CAPITAL:
                self._validar_custeio_para_capital(rateio, rateio_atual, sem_exigencia_especificacao)

        return ctx

    def apply(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """R21 — Reseta campos incompatíveis quando a aplicação do rateio muda.

        Migrado de DespesaService._atualizar_rateios() — blocos "CAPITAL -> CUSTEIO"
        e "CUSTEIO -> CAPITAL" que chamavam rateio.update({...}).
        """
        if not ctx.despesa_instance:
            return ctx

        despesa = ctx.despesa_instance

        for rateio in ctx.rateios:
            if "uuid" not in rateio:
                continue

            rateio_atual = RateioDespesa.objects.filter(uuid=rateio["uuid"]).first()
            if not rateio_atual:
                continue

            aplicacao_anterior = rateio_atual.aplicacao_recurso
            nova_aplicacao = rateio.get("aplicacao_recurso")

            if aplicacao_anterior == nova_aplicacao:
                continue

            saida_recurso_externo = rateio.get(
                "saida_de_recurso_externo",
                rateio_atual.saida_de_recurso_externo,
            )
            sem_exigencia = despesa.eh_despesa_sem_comprovacao_fiscal or saida_recurso_externo

            if aplicacao_anterior == APLICACAO_CAPITAL and nova_aplicacao == APLICACAO_CUSTEIO:
                self._resetar_campos_capital(rateio, sem_exigencia)
            elif aplicacao_anterior == APLICACAO_CUSTEIO and nova_aplicacao == APLICACAO_CAPITAL:
                self._resetar_campos_custeio(rateio, sem_exigencia)

        return ctx

    @staticmethod
    def _validar_capital_para_custeio(rateio: dict, sem_exigencia: bool) -> None:
        """R17, R18."""
        if sem_exigencia:
            return

        tipo_custeio = rateio.get("tipo_custeio")
        especificacao = rateio.get("especificacao_material_servico")

        if not tipo_custeio or not especificacao:
            raise DespesaValidationError({
                "mensagem": (
                    "Ao alterar o tipo de aplicação de Capital para Custeio, "
                    "é obrigatório informar o Tipo de Custeio e a Especificação de "
                    "Material ou Serviço em cada rateio."
                )
            })

        if especificacao.aplicacao_recurso != APLICACAO_CUSTEIO:
            raise DespesaValidationError({
                "mensagem": (
                    "Ao alterar o tipo de aplicação de Capital para Custeio, "
                    "é obrigatório informar uma Especificação de Material ou Serviço "
                    "de Custeio. A especificação atual é de Capital."
                )
            })

    @staticmethod
    def _validar_custeio_para_capital(rateio: dict, rateio_atual, sem_exigencia: bool) -> None:
        """R19, R20."""
        if sem_exigencia:
            return

        especificacao = rateio.get("especificacao_material_servico")
        if especificacao is None:
            especificacao = rateio_atual.especificacao_material_servico

        if not especificacao:
            raise DespesaValidationError({
                "mensagem": (
                    "Ao alterar o tipo de aplicação de Custeio para Capital, "
                    "é obrigatório informar a Especificação de Material ou Serviço "
                    "de Capital em cada rateio."
                )
            })

        if especificacao.aplicacao_recurso != APLICACAO_CAPITAL:
            raise DespesaValidationError({
                "mensagem": (
                    "Ao alterar o tipo de aplicação de Custeio para Capital, "
                    "é obrigatório informar uma Especificação de Material ou Serviço "
                    "de Capital. A especificação atual é de Custeio."
                )
            })

    @staticmethod
    def _resetar_campos_capital(rateio: dict, sem_exigencia: bool) -> None:
        """R21 — Limpa campos de CAPITAL ao migrar para CUSTEIO."""
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
        """R21 — Limpa campos de CUSTEIO ao migrar para CAPITAL."""
        updates = {"tipo_custeio": None}
        if sem_exigencia:
            updates["especificacao_material_servico"] = None
        rateio.update(updates)
