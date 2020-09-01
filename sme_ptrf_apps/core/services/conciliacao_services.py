from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.receitas.models import Receita


def receitas_conciliadas_por_conta_e_acao_na_conciliacao(conta_associacao, acao_associacao, periodo):
    dataset = periodo.receitas_conciliadas_no_periodo.filter(conta_associacao=conta_associacao).filter(
        acao_associacao=acao_associacao)

    return dataset.all()


def info_conciliacao_pendente(periodo, conta_associacao):
    acoes_associacao = Associacao.acoes_da_associacao(associacao_uuid=conta_associacao.associacao.uuid)
    result = []
    for acao_associacao in acoes_associacao:
        info_acao = info_conciliacao_acao_associacao_no_periodo(acao_associacao=acao_associacao,
                                                                periodo=periodo,
                                                                conta_associacao=conta_associacao)

        info = {
            'acao_associacao_uuid': f'{acao_associacao.uuid}',
            'acao_associacao_nome': acao_associacao.acao.nome,

            'receitas_no_periodo': info_acao['receitas_no_periodo'],

            'despesas_no_periodo': info_acao['despesas_no_periodo'],

            'despesas_nao_conciliadas': info_acao['despesas_nao_conciliadas'],

            'receitas_nao_conciliadas': info_acao['receitas_nao_conciliadas'],

        }
        result.append(info)

    return result


def info_conciliacao_acao_associacao_no_periodo(acao_associacao, periodo, conta_associacao):
    def resultado_vazio():
        return {
            'receitas_no_periodo': 0,
            'despesas_no_periodo': 0,
            'receitas_nao_conciliadas': 0,
            'despesas_nao_conciliadas': 0,
        }

    def sumariza_conciliacao_receitas_do_periodo_e_acao(periodo, conta_associacao, acao_associacao, info):

        receitas_conciliadas = receitas_conciliadas_por_conta_e_acao_na_conciliacao(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=periodo)

        for receita_conciliada in receitas_conciliadas:
            info['receitas_no_periodo'] += receita_conciliada.valor

        receitas_nao_conciliadas = receitas_nao_conciliadas_por_conta_e_acao_no_periodo(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=periodo)

        for receita_nao_conciliada in receitas_nao_conciliadas:
            info['receitas_no_periodo'] += receita_nao_conciliada.valor
            info['receitas_nao_conciliadas'] += receita_nao_conciliada.valor

        return info

    def sumariza_conciliacao_despesas_do_periodo_e_acao(periodo, conta_associacao, acao_associacao, info, ):
        rateios_conciliados = despesas_conciliadas_por_conta_e_acao_na_conciliacao(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=periodo)

        for rateio_conciliado in rateios_conciliados:
            info['despesas_no_periodo'] += rateio_conciliado.valor_rateio

        rateios_nao_conciliados = despesas_nao_conciliadas_por_conta_e_acao_no_periodo(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=periodo)

        for rateio_nao_conciliado in rateios_nao_conciliados:
            info['despesas_no_periodo'] += rateio_nao_conciliado.valor_rateio
            info['despesas_nao_conciliadas'] += rateio_nao_conciliado.valor_rateio

        return info

    info = resultado_vazio()

    info = sumariza_conciliacao_receitas_do_periodo_e_acao(periodo=periodo,
                                                           conta_associacao=conta_associacao,
                                                           acao_associacao=acao_associacao,
                                                           info=info)

    info = sumariza_conciliacao_despesas_do_periodo_e_acao(periodo=periodo,
                                                           conta_associacao=conta_associacao,
                                                           acao_associacao=acao_associacao, info=info)

    return info


def despesas_nao_conciliadas_por_conta_e_acao_no_periodo(conta_associacao, acao_associacao, periodo):
    dataset = RateioDespesa.objects.filter(conta_associacao=conta_associacao).filter(
        acao_associacao=acao_associacao).filter(conferido=False)

    # No caso de despesas não conciliadas todas devem ser exibidas até a data limite do período
    if periodo.data_fim_realizacao_despesas:
        dataset = dataset.filter(despesa__data_documento__lte=periodo.data_fim_realizacao_despesas)

    return dataset.all()


def despesas_conciliadas_por_conta_e_acao_na_conciliacao(conta_associacao, acao_associacao, periodo):
    dataset = periodo.despesas_conciliadas_no_periodo.filter(conta_associacao=conta_associacao).filter(
        acao_associacao=acao_associacao)

    return dataset.all()


def receitas_nao_conciliadas_por_conta_e_acao_no_periodo(conta_associacao, acao_associacao, periodo):
    dataset = Receita.objects.filter(conta_associacao=conta_associacao).filter(acao_associacao=acao_associacao).filter(
        conferido=False)

    # No caso de despesas não conciliadas todas devem ser exibidas até a data limite do período
    if periodo.data_fim_realizacao_despesas:
        dataset = dataset.filter(data__lte=periodo.data_fim_realizacao_despesas)

    return dataset.all()


def receitas_conciliadas_por_conta_e_acao_no_periodo(conta_associacao, acao_associacao, periodo):
    dataset = Receita.objects.filter(conta_associacao=conta_associacao).filter(acao_associacao=acao_associacao).filter(
        conferido=True)

    if periodo.data_fim_realizacao_despesas:
        dataset = dataset.filter(
            data__range=(periodo.data_inicio_realizacao_despesas, periodo.data_fim_realizacao_despesas))
    else:
        dataset = dataset.filter(data__gte=periodo.data_inicio_realizacao_despesas)

    return dataset.all()


