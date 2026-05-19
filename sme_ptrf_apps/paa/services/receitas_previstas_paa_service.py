from django.db import transaction
from sme_ptrf_apps.core.models import Associacao, Recurso
from sme_ptrf_apps.core.models.periodo import Periodo
from sme_ptrf_apps.paa.models import ReceitaPrevistaPaa
from sme_ptrf_apps.core.services.resumo_rescursos_service import ResumoRecursosService


class SaldosPorAcaoPaaService:
    def __init__(self, paa, associacao):
        self.paa = paa
        self.associacao = associacao

    def _limpar_prioridades_impactadas_despesas(self, receita_prevista):
        from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasReceitasPrevistasPTRFService
        # Considerando o cenário em que despesas podem ser criadas enquanto um saldo é congelado e
        # posteriormente, descongelado, o saldo das prioridades podem ser impactados pela negativação
        # por isso, o campo valor_total das prioridades devem ser limpos
        PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            {}, receita_prevista).limpar_valor_prioridades_saldo_indisponivel_da_acao_receita()

    @transaction.atomic
    def descongelar_saldos(self):
        self.paa.set_descongelar_saldo()

        receitas_previstas = []
        acoes_associacao = Associacao.acoes_da_associacao(associacao_uuid=self.associacao.uuid)

        for acao in acoes_associacao:
            receita_prevista, _ = ReceitaPrevistaPaa.objects.update_or_create(
                paa=self.paa,
                acao_associacao=acao,
                defaults={
                    "saldo_congelado_custeio": None,
                    "saldo_congelado_capital": None,
                    "saldo_congelado_livre": None,
                }
            )

            receitas_previstas.append(receita_prevista)
            self._limpar_prioridades_impactadas_despesas(receita_prevista)

        return receitas_previstas

    @transaction.atomic
    def congelar_saldos(self):
        # Congela o saldo somente se ele ainda não foi congelado. Evita o "recongelamento"(atualiza para o valor atual)
        if self.paa.saldo_congelado_em:
            return []

        self.paa.set_congelar_saldo()
        recurso = Recurso.objects.filter(legado=True).first()
        self.periodo = Periodo.da_data_por_recurso(self.paa.saldo_congelado_em, recurso=recurso)
        if not self.periodo:
            raise Exception('Não foi possivel encontrar o período relacionado à data de congelamento do saldo.')
        receitas_previstas = []
        acoes_associacao = Associacao.acoes_da_associacao(associacao_uuid=self.associacao.uuid)

        for acao in acoes_associacao:
            resumo = ResumoRecursosService.resumo_recursos(
                periodo=self.periodo,
                acao_associacao=acao,
                data_fim=self.paa.saldo_congelado_em
            )
            # Havendo saldo negativo no valor reprogramado, o saldo congelado deve ser zerado
            saldo_custeio = resumo.saldo_posterior.total_custeio
            saldo_capital = resumo.saldo_posterior.total_capital
            saldo_livre = resumo.saldo_posterior.total_livre

            receita_prevista, _ = ReceitaPrevistaPaa.objects.update_or_create(
                paa=self.paa,
                acao_associacao=acao,
                defaults={
                    "saldo_congelado_custeio": saldo_custeio if saldo_custeio >= 0 else 0,
                    "saldo_congelado_capital": saldo_capital if saldo_capital >= 0 else 0,
                    "saldo_congelado_livre": saldo_livre if saldo_livre >= 0 else 0,
                }
            )

            receitas_previstas.append(receita_prevista)

        return receitas_previstas
