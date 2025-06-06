from django.db import transaction
from django.core.exceptions import ValidationError
from sme_ptrf_apps.core.models import Associacao, AcaoAssociacao
from sme_ptrf_apps.core.models.periodo import Periodo
from sme_ptrf_apps.paa.models import ReceitaPrevistaPaa
from sme_ptrf_apps.core.services.resumo_rescursos_service import ResumoRecursosService


def associacoes_nao_vinculadas_a_acao(acao):
    associacoes_vinculadas = acao.associacoes_da_acao.values_list('associacao__id', flat=True)
    result = Associacao.objects.exclude(id__in=associacoes_vinculadas)
    return result


def validate_acao_associacao(associacao, acao, instance=None):
    existing_records = AcaoAssociacao.objects.filter(
        associacao=associacao,
        acao=acao,
        status=AcaoAssociacao.STATUS_ATIVA
    ).exclude(pk=instance.pk if instance else None)

    if existing_records.exists():
        raise ValidationError('Já existe um registro com a mesma associação e ação com status ativa')


def obter_saldos_periodo_atual(acao_associacao):
    periodo = Periodo.periodo_atual()

    resumo = ResumoRecursosService.resumo_recursos(
        periodo=periodo,
        acao_associacao=acao_associacao,
    )

    saldos = {
        "saldo_atual_custeio": resumo.saldo_posterior.total_custeio,
        "saldo_atual_capital": resumo.saldo_posterior.total_capital,
        "saldo_atual_livre": resumo.saldo_posterior.total_livre,
    }

    return saldos


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
