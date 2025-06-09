from django.core.exceptions import ValidationError
from sme_ptrf_apps.core.models import Associacao, AcaoAssociacao
from sme_ptrf_apps.core.models.periodo import Periodo
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
