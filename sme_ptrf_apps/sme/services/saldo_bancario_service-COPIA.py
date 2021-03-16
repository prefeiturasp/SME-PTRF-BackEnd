import logging

from django.db.models import Count, Sum, F, Q

from sme_ptrf_apps.core.models import ObservacaoConciliacao, Associacao, Unidade

logger = logging.getLogger(__name__)


def saldo_por_tipo_de_unidade(queryset, periodo, conta):
    # saldos = [
    #     {"tipo_unidade": "CEU", "qtd_informada": 100, "saldo": 1000},
    #     {"tipo_unidade": "EMEF", "qtd_informada": 100, "saldo": 1000},
    # ]
    #
    # totais = [
    #     {"tipo_unidade": "CEU", "total_unidades": 100},
    #     {"tipo_unidade": "EMEF", "total_unidades": 100},
    #     {"tipo_unidade": "EMEI", "total_unidades": 100},
    # ]
    #
    # result = {
    #     "CEU": {"qtd_informada": 0, "saldo": 0, "total_unidades": 0},
    #     "EMEF": {"qtd_informada": 0, "saldo": 0, "total_unidades": 0},
    #     "EMEI": {"qtd_informada": 0, "saldo": 0, "total_unidades": 0},
    # }
    #
    # vazio = {"qtd_informada": 0, "saldo": 0, "total_unidades": 0}
    #
    # result = dict()
    # for tipo in choices:
    #     result[tipo] = vazio
    #
    # for saldo in saldos:
    #     result[saldo["tipo_unidade"]]["qtd_informada"] = saldo["qtd_informada"]
    #     result[saldo["tipo_unidade"]]["saldo"] = saldo["saldo"]
    #
    # for total in totais:
    #     result[total["tipo_unidade"]]["total_unidades"] = total["total_unidades"]


    saldo_por_tipo_unidade = queryset.filter(
        periodo__uuid=periodo,
        conta_associacao__tipo_conta__uuid=conta
    ).values('associacao__unidade__tipo_unidade').annotate(
        qtde_unidades_informadas=Count('uuid'), saldo_bancario_informado=Sum('saldo_extrato')
    )

    total_unidades_por_tipo = Associacao.objects.all().values('unidade__tipo_unidade').annotate(qtde=Count('uuid'))

    vazio = {"qtde_unidades_informadas": 0, "saldo_bancario_informado": 0, "total_unidades": 0}

    result = dict()

    choices = Unidade.objects.values_list('tipo_unidade', flat=True).distinct()

    for tipo in choices:
        result[tipo] = {"qtde_unidades_informadas": 0, "saldo_bancario_informado": 0, "total_unidades": 0}

    for total in total_unidades_por_tipo:
        print(f'NOME: {total["unidade__tipo_unidade"]} Valor: {total["qtde"]}')
        result[total["unidade__tipo_unidade"]]["total_unidades"] = total["qtde"]


    print(f'AQUI XXXXXX {result}')


    # for saldo in saldo_por_tipo_unidade:
    #     result[saldo["associacao__unidade__tipo_unidade"]]["qtde_unidades_informadas"] = saldo["qtde_unidades_informadas"]
    #     result[saldo["associacao__unidade__tipo_unidade"]]["saldo_bancario_informado"] = saldo["saldo_bancario_informado"]


    # print(f'AQUI XXXXXX {result}')

    # for saldo in saldo_por_tipo_unidade:
    #     tipo_unidade = saldo['associacao__unidade__tipo_unidade']
    #     valores_por_tipo[saldo['associacao__unidade__tipo_unidade']]['qtde_unidades_informadas'] = saldo['qtde_unidades_informadas']
    #     valores_por_tipo[saldo['associacao__unidade__tipo_unidade']]['saldo_bancario_informado'] = saldo['saldo_bancario_informado']
    #
    # for total in total_unidades_por_tipo:
    #     valores_por_tipo[total['unidade__tipo_unidade']]['qtde'] = total['qtde']
    #
    # print(f'AQUI XXXXXX {valores_por_tipo}')

    objeto_completo = [
        saldo_por_tipo_unidade,
        total_unidades_por_tipo,
        result
    ]




    return objeto_completo

