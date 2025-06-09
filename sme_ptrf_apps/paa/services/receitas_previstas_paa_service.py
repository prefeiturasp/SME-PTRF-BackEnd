from django.db import transaction
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.core.models.periodo import Periodo
from sme_ptrf_apps.paa.models import ReceitaPrevistaPaa
from sme_ptrf_apps.core.services.resumo_rescursos_service import ResumoRecursosService


class SaldosPorAcaoPaaService:
    def __init__(self, paa, associacao):
        self.paa = paa
        self.associacao = associacao

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

        return receitas_previstas

    @transaction.atomic
    def congelar_saldos(self):
        self.paa.set_congelar_saldo()
        self.periodo = Periodo.da_data(self.paa.saldo_congelado_em)

        receitas_previstas = []
        acoes_associacao = Associacao.acoes_da_associacao(associacao_uuid=self.associacao.uuid)

        for acao in acoes_associacao:
            resumo = ResumoRecursosService.resumo_recursos(
                periodo=self.periodo,
                acao_associacao=acao,
                data_fim=self.paa.saldo_congelado_em
            )

            receita_prevista, _ = ReceitaPrevistaPaa.objects.update_or_create(
                paa=self.paa,
                acao_associacao=acao,
                defaults={
                    "saldo_congelado_custeio": resumo.saldo_posterior.total_custeio,
                    "saldo_congelado_capital": resumo.saldo_posterior.total_capital,
                    "saldo_congelado_livre": resumo.saldo_posterior.total_livre,
                }
            )

            receitas_previstas.append(receita_prevista)

        return receitas_previstas
