import logging

from django.db.models import Count, Sum

from sme_ptrf_apps.core.models import Associacao, Unidade

logger = logging.getLogger(__name__)


def saldo_por_tipo_de_unidade(queryset, periodo, conta):
    saldo_por_tipo_unidade = queryset.filter(
        periodo__uuid=periodo,
        conta_associacao__tipo_conta__uuid=conta
    ).values('associacao__unidade__tipo_unidade').annotate(
        qtde_unidades_informadas=Count('uuid'), saldo_bancario_informado=Sum('saldo_extrato')
    )

    total_unidades_por_tipo = Associacao.objects.exclude(cnpj__exact='').values('unidade__tipo_unidade').annotate(qtde=Count('uuid'))

    choices = Unidade.TIPOS_CHOICE

    result = dict()

    for tipo in choices:
        result[tipo[0]] = {"tipo_de_unidade": tipo[0], "qtde_unidades_informadas": 0, "saldo_bancario_informado": 0, "total_unidades": 0}

    for total in total_unidades_por_tipo:
        result[total["unidade__tipo_unidade"]]["total_unidades"] = total["qtde"]

    for saldo in saldo_por_tipo_unidade:
        result[saldo["associacao__unidade__tipo_unidade"]]["qtde_unidades_informadas"] = saldo["qtde_unidades_informadas"]
        result[saldo["associacao__unidade__tipo_unidade"]]["saldo_bancario_informado"] = saldo["saldo_bancario_informado"]

    lista_de_saldos_bancarios_por_tipo = []

    for valor in result.values():
        lista_de_saldos_bancarios_por_tipo.append(valor)

    return lista_de_saldos_bancarios_por_tipo

