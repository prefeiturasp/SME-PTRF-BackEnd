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
