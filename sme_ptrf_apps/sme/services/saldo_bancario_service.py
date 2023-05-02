import logging
import datetime

from django.db.models import Count, Sum, Q, FilteredRelation
from django.contrib.auth import get_user_model

from sme_ptrf_apps.core.models import Associacao, Unidade, Periodo, TipoConta
from sme_ptrf_apps.core.choices.tipos_unidade import TIPOS_CHOICE
from sme_ptrf_apps.core.models.parametros import Parametros

logger = logging.getLogger(__name__)


def saldo_por_tipo_de_unidade(queryset, periodo, conta):
    saldo_por_tipo_unidade = queryset.filter(
        periodo__uuid=periodo.uuid,
        conta_associacao__tipo_conta__uuid=conta
    ).values('associacao__unidade__tipo_unidade').annotate(
        qtde_unidades_informadas=Count('uuid'), saldo_bancario_informado=Sum('saldo_extrato')
    )

    total_unidades_por_tipo = Associacao.get_associacoes_ativas_no_periodo(periodo=periodo).values('unidade__tipo_unidade').annotate(
        qtde=Count('uuid'))

    choices = TIPOS_CHOICE

    result = dict()

    for tipo in choices:
        if tipo[0].upper() != 'ADM' and tipo[0].upper() != 'DRE':
            result[tipo[0]] = {"tipo_de_unidade": tipo[0], "qtde_unidades_informadas": 0, "saldo_bancario_informado": 0,
                               "total_unidades": 0}

    for total in total_unidades_por_tipo:
        result[total["unidade__tipo_unidade"]]["total_unidades"] = total["qtde"]

    for saldo in saldo_por_tipo_unidade:
        result[saldo["associacao__unidade__tipo_unidade"]]["qtde_unidades_informadas"] = saldo[
            "qtde_unidades_informadas"]
        result[saldo["associacao__unidade__tipo_unidade"]]["saldo_bancario_informado"] = saldo[
            "saldo_bancario_informado"]

    lista_de_saldos_bancarios_por_tipo = []

    for valor in result.values():
        lista_de_saldos_bancarios_por_tipo.append(valor)

    return lista_de_saldos_bancarios_por_tipo


def saldo_por_dre(queryset, periodo, conta):
    saldo_por_dre = queryset.filter(
        periodo__uuid=periodo.uuid,
        conta_associacao__tipo_conta__uuid=conta
    ).values('associacao__unidade__dre', 'associacao__unidade__dre__nome').annotate(
        qtde_dre_informadas=Count('uuid'), saldo_bancario_informado=Sum('saldo_extrato')
    )

    total_unidades_por_dre = Associacao.objects.exclude(cnpj__exact='').values('unidade__dre','unidade__dre__nome').annotate(qtde=Count('uuid'))

    total_unidades_por_dre_dict = {}
    for unidade in total_unidades_por_dre:
        unidade['qtde'] = 0
        unidade['qtd'] = 0
        total_unidades_por_dre_dict[unidade['unidade__dre']] = unidade

    total_unidades_por_dre_associacao_ativa = Associacao.get_associacoes_ativas_no_periodo(periodo=periodo).values('unidade__dre','unidade__dre__nome').annotate(qtde=Count('uuid'))

    for unidade in total_unidades_por_dre_associacao_ativa:
        if unidade['unidade__dre'] in total_unidades_por_dre_dict:
            total_unidades_por_dre_dict[unidade['unidade__dre']]['qtde'] = unidade['qtde']

    total_unidades_por_dre_dict_list = list(total_unidades_por_dre_dict.values())

    result = dict()
    
    for nome in total_unidades_por_dre_dict_list:
        if nome['unidade__dre'] is not None and nome['unidade__dre__nome'] is not None:
            result[nome['unidade__dre']] = {"nome_dre": nome['unidade__dre__nome'], "qtde_dre_informadas": 0,
                                            "saldo_bancario_informado": 0, "total_unidades": 0}

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
    choices = []
    result = dict()
    dres = Unidade.dres.exclude(sigla='')
    tupla_choices = TIPOS_CHOICE

    for choice in tupla_choices:
        if choice[0].upper() != 'DRE' and choice[0].upper() != 'ADM':
            choices.append(choice[0])

    for dre in dres:

        if Parametros.get().desconsiderar_associacoes_nao_iniciadas:
            saldo_por_tipo_da_dre = queryset.filter(
                Q(associacao__periodo_inicial__isnull=False) & 
                Q(associacao__periodo_inicial__referencia__lt=periodo.referencia) & (
                    Q(associacao__data_de_encerramento__isnull=True) | Q(associacao__data_de_encerramento__gt=periodo.data_inicio_realizacao_despesas)
                ),
                periodo__uuid=periodo.uuid,
                conta_associacao__tipo_conta__uuid=conta,
                associacao__unidade__dre=dre
            ).values('associacao__unidade__tipo_unidade', 'associacao__unidade__dre__sigla').annotate(
                saldo_bancario_informado=Sum('saldo_extrato')
            )
        else:
            saldo_por_tipo_da_dre = queryset.filter(
                periodo__uuid=periodo.uuid,
                conta_associacao__tipo_conta__uuid=conta,
                associacao__unidade__dre=dre
            ).values('associacao__unidade__tipo_unidade', 'associacao__unidade__dre__sigla').annotate(
                saldo_bancario_informado=Sum('saldo_extrato')
            )
        saldos_por_ue_dre.extend(saldo_por_tipo_da_dre)

        result[dre.sigla] = {"sigla_dre": dre.sigla, "uuid_dre": dre.uuid, "associacoes": []}

        for tipo in choices:
            result[dre.sigla]['associacoes'].append({"associacao": tipo, "saldo_total": 0})

    for saldo in saldos_por_ue_dre:
        for r in result[saldo['associacao__unidade__dre__sigla']]['associacoes']:
            if r['associacao'] in saldo['associacao__unidade__tipo_unidade']:
                r['saldo_total'] = saldo['saldo_bancario_informado']

    lista_de_saldos_bancarios_ue_dre = []

    for valor in result.values():
        lista_de_saldos_bancarios_ue_dre.append(valor)

    return lista_de_saldos_bancarios_ue_dre


def saldo_detalhe_associacao(periodo, conta_uuid, dre_uuid, unidade, tipo_ue):
    dres = Unidade.dres.exclude(sigla='')

    dre = dres.get(uuid=dre_uuid)

    filtered_relation = FilteredRelation(
        'observacoes_conciliacao_da_associacao',
        condition=Q(observacoes_conciliacao_da_associacao__periodo=periodo)
    )

    qs = Associacao.get_associacoes_ativas_no_periodo(periodo=periodo).filter(unidade__dre__sigla=dre.sigla).annotate(
        obs_periodo=filtered_relation
    ).filter(
        Q(obs_periodo__conta_associacao__tipo_conta__uuid=conta_uuid) | Q(obs_periodo__isnull=True)
    ).values(
        'nome',
        'unidade__codigo_eol',
        'obs_periodo__saldo_extrato',
        'obs_periodo__data_extrato',
        'obs_periodo__comprovante_extrato',
        'obs_periodo__uuid',
    )

    # Filtros
    if unidade is not None:
        qs = qs.filter(Q(nome__unaccent__icontains=unidade) | Q(
            unidade__nome__unaccent__icontains=unidade) | Q(
            unidade__codigo_eol__icontains=unidade))
        return qs

    if tipo_ue is not None:
        qs = qs.filter(Q(unidade__tipo_unidade__icontains=tipo_ue))
        return qs

    return qs


def gerar_dados_extrato_dres_exportacao_xlsx(periodo_uuid, conta_uuid, username):
    periodo_relation = Periodo.objects.get(uuid=periodo_uuid)
    data_inicio = formata_data(periodo_relation.data_inicio_realizacao_despesas)
    data_fim = formata_data(periodo_relation.data_fim_realizacao_despesas)
    periodo = f"{periodo_relation.referencia} - {data_inicio} até {data_fim}"

    conta = TipoConta.objects.get(uuid=conta_uuid)

    usuario = get_user_model().objects.get(username=username)

    filtered_relation = FilteredRelation(
        'observacoes_conciliacao_da_associacao',
        condition=Q(observacoes_conciliacao_da_associacao__periodo=periodo_relation)
    )

    qs = Associacao.objects.annotate(
        obs_periodo=filtered_relation
    ).filter(
        Q(obs_periodo__conta_associacao__tipo_conta__uuid=conta_uuid) | Q(obs_periodo__isnull=True)
    ).values(
        'unidade__codigo_eol',
        'unidade__nome',
        'unidade__tipo_unidade',
        'unidade__dre__nome',
        'obs_periodo__data_extrato',
        'obs_periodo__saldo_extrato',
    ).order_by('unidade__dre__nome')

    dados = {
        "qs": qs,
        "informacoes_adicionais": {
            "periodo": periodo,
            "conta": conta.nome,
            "usuario": usuario.name,
            "filtro": f"Filtrado por período {periodo} e por conta {str(conta).lower()}"
        }
    }

    return dados


def formata_data(data):
    original_date = datetime.datetime.strptime(str(data), '%Y-%m-%d')
    formatted_date = original_date.strftime("%d/%m/%Y")
    return formatted_date
