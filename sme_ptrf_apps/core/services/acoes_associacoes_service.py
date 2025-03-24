from django.core.exceptions import ValidationError
from ..models import Associacao, AcaoAssociacao


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
    from sme_ptrf_apps.core.services.painel_resumo_recursos_service import PainelResumoRecursosService
    from ..models import Periodo

    periodo = Periodo.periodo_atual()
    painel = PainelResumoRecursosService.painel_resumo_recursos(
        acao_associacao.associacao,
        periodo
    )
    info_da_acao_associacao = next(filter(lambda x: x.acao_associacao_uuid == acao_associacao.uuid, painel.info_acoes), None)
    saldos = {}
    saldos["saldo_atual_total"] = info_da_acao_associacao.saldo_atual_total
    saldos["saldo_atual_capital"] = info_da_acao_associacao.saldo_atual_capital
    saldos["saldo_atual_custeio"] = info_da_acao_associacao.saldo_atual_custeio
    saldos["saldo_atual_livre"] = info_da_acao_associacao.saldo_atual_livre

    return saldos
