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


def saldo_por_dre(queryset, periodo, conta):
    saldo_por_dre = queryset.filter(
        periodo__uuid=periodo,
        conta_associacao__tipo_conta__uuid=conta
    ).values('associacao__unidade__dre', 'associacao__unidade__dre__nome').annotate(
        qtde_dre_informadas=Count('uuid'), saldo_bancario_informado=Sum('saldo_extrato')
    )

    total_unidades_por_dre = Associacao.objects.exclude(cnpj__exact='').values('unidade__dre', 'unidade__dre__nome').annotate(
        qtde=Count('uuid'))

    result = dict()

    for nome in total_unidades_por_dre:
        result[nome['unidade__dre']] = {"nome_dre": nome['unidade__dre__nome'], "qtde_dre_informadas": 0, "saldo_bancario_informado": 0, "total_unidades": 0}
        result[nome["unidade__dre"]]["total_unidades"] = nome["qtde"]

    for saldo in saldo_por_dre:
        result[saldo["associacao__unidade__dre"]]["qtde_dre_informadas"] = saldo["qtde_dre_informadas"]
        result[saldo["associacao__unidade__dre"]]["saldo_bancario_informado"] = saldo["saldo_bancario_informado"]

    lista_de_saldos_bancarios_dre = []

    for valor in result.values():
        lista_de_saldos_bancarios_dre.append(valor)

    return lista_de_saldos_bancarios_dre


def saldo_por_ue_dre(queryset, periodo, conta):
    saldos_por_ue_dre = []

    # for dre in Unidade.dres.all():
    #     saldo_por_tipo_da_dre = queryset.filter(
    #         periodo__uuid=periodo,
    #         conta_associacao__tipo_conta__uuid=conta,
    #         associacao__unidade__dre = dre
    #     ).values('associacao__unidade__tipo_unidade', 'associacao__unidade__dre', 'associacao__unidade__dre__sigla').annotate(
    #         saldo_bancario_informado=Sum('saldo_extrato')
    #     )
    #     saldos_por_ue_dre.append(saldo_por_tipo_da_dre)

    dres = Unidade.dres.all()

    result = dict()

    por_dre = dict()

    for dre in dres:
        result[dre.sigla] = {"associacao__unidade__tipo_unidade": '', "associacao__unidade__dre__sigla": dre.sigla, "saldo_bancario_informado": 0}
        por_dre[dre.sigla] = Associacao.objects.filter(unidade__dre__sigla=dre.sigla).values_list('unidade__tipo_unidade', flat=True).order_by().distinct()

    print(f'XXXXXX {por_dre}')

    unidades_por_tipo = Associacao.objects.exclude(cnpj__exact='').values('unidade__dre__sigla', 'unidade__tipo_unidade').order_by().distinct()

    for unidade in unidades_por_tipo:
        #print(f"Unidade {unidade}")
        result[unidade['unidade__dre__sigla']] = {"associacao__unidade__tipo_unidade": unidade['unidade__tipo_unidade'], "associacao__unidade__dre__sigla": unidade['unidade__dre__sigla'], "saldo_bancario_informado": 0}

    for dre in dres:
        saldo_por_tipo_da_dre = queryset.filter(
            periodo__uuid=periodo,
            conta_associacao__tipo_conta__uuid=conta,
            associacao__unidade__dre = dre
        ).values('associacao__unidade__tipo_unidade', 'associacao__unidade__dre__sigla').annotate(
            saldo_bancario_informado=Sum('saldo_extrato')
        )
        saldos_por_ue_dre.extend(saldo_por_tipo_da_dre)

    for saldo in saldos_por_ue_dre:
         result[saldo["associacao__unidade__dre__sigla"]]["saldo_bancario_informado"] = saldo["saldo_bancario_informado"]
         result[saldo["associacao__unidade__dre__sigla"]]["associacao__unidade__tipo_unidade"] = saldo["associacao__unidade__tipo_unidade"]


    lista_de_saldos_bancarios_ue_dre = []

    for valor in result.values():
        lista_de_saldos_bancarios_ue_dre.append(valor)

    return lista_de_saldos_bancarios_ue_dre
    # return saldos_por_ue_dre


