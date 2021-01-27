from ..models import Associacao


def associacoes_nao_vinculadas_a_acao(acao):
    associacoes_vinculadas = acao.associacoes_da_acao.values_list('associacao__id', flat=True)
    result = Associacao.objects.exclude(id__in=associacoes_vinculadas)
    return result
