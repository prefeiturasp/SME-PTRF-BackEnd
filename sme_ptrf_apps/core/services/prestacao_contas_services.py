from ..models import PrestacaoConta, ContaAssociacao, Periodo, AcaoAssociacao, FechamentoPeriodo, Associacao
from ..services import info_acoes_associacao_no_periodo
from ...despesas.models import RateioDespesa
from ...receitas.models import Receita


def iniciar_prestacao_de_contas(conta_associacao_uuid, periodo_uuid):
    conta_associacao = ContaAssociacao.objects.get(uuid=conta_associacao_uuid)
    periodo = Periodo.by_uuid(periodo_uuid)

    return PrestacaoConta.iniciar(conta_associacao=conta_associacao, periodo=periodo)


def concluir_prestacao_de_contas(prestacao_contas_uuid, observacoes):
    prestacao = PrestacaoConta.concluir(uuid=prestacao_contas_uuid, observacoes=observacoes)

    associacao = prestacao.associacao
    periodo = prestacao.periodo
    acoes = associacao.acoes.filter(status=AcaoAssociacao.STATUS_ATIVA)

    for acao in acoes:
        totais_receitas = Receita.totais_por_acao_associacao_no_periodo(acao_associacao=acao, periodo=periodo)
        totais_despesas = RateioDespesa.totais_por_acao_associacao_no_periodo(acao_associacao=acao, periodo=periodo)
        especificacoes_despesas = RateioDespesa.especificacoes_dos_rateios_da_acao_associacao_no_periodo(
            acao_associacao=acao, periodo=periodo)
        FechamentoPeriodo.criar(
            prestacao_conta=prestacao,
            acao_associacao=acao,
            total_receitas_capital=totais_receitas['total_receitas_capital'],
            total_repasses_capital=totais_receitas['total_repasses_capital'],
            total_receitas_custeio=totais_receitas['total_receitas_custeio'],
            total_repasses_custeio=totais_receitas['total_repasses_custeio'],
            total_despesas_capital=totais_despesas['total_despesas_capital'],
            total_despesas_custeio=totais_despesas['total_despesas_custeio'],
            total_receitas_nao_conciliadas_capital=totais_receitas['total_receitas_nao_conciliadas_capital'],
            total_receitas_nao_conciliadas_custeio=totais_receitas['total_receitas_nao_conciliadas_custeio'],
            total_despesas_nao_conciliadas_capital=totais_despesas['total_despesas_nao_conciliadas_capital'],
            total_despesas_nao_conciliadas_custeio=totais_despesas['total_despesas_nao_conciliadas_custeio'],
            especificacoes_despesas=especificacoes_despesas
        )

    return prestacao


def salvar_prestacao_de_contas(prestacao_contas_uuid, observacoes):
    return PrestacaoConta.salvar(uuid=prestacao_contas_uuid, observacoes=observacoes)


def revisar_prestacao_de_contas(prestacao_contas_uuid, motivo):
    prestacao = PrestacaoConta.revisar(uuid=prestacao_contas_uuid, motivo=motivo)

    return prestacao


def informacoes_financeiras_para_atas(prestacao_contas):
    def totaliza_info_acoes(info_acoes):
        totalizador = {
            'saldo_reprogramado': 0,
            'saldo_reprogramado_capital': 0,
            'saldo_reprogramado_custeio': 0,
            'receitas_no_periodo': 0,
            'repasses_no_periodo': 0,
            'repasses_no_periodo_capital': 0,
            'repasses_no_periodo_custeio': 0,
            'outras_receitas_no_periodo': 0,
            'outras_receitas_no_periodo_capital': 0,
            'outras_receitas_no_periodo_custeio': 0,
            'despesas_no_periodo': 0,
            'despesas_no_periodo_capital': 0,
            'despesas_no_periodo_custeio': 0,
            'despesas_nao_conciliadas': 0,
            'despesas_nao_conciliadas_capital': 0,
            'despesas_nao_conciliadas_custeio': 0,
            'receitas_nao_conciliadas': 0,
            'receitas_nao_conciliadas_capital': 0,
            'receitas_nao_conciliadas_custeio': 0,
            'saldo_atual_custeio': 0,
            'saldo_atual_capital': 0,
            'saldo_atual_total': 0,
        }
        for info_acao in info_acoes:
            for key in totalizador.keys():
                totalizador[key] += info_acao[key]

        return totalizador

    info_acoes = info_acoes_associacao_no_periodo(associacao_uuid=prestacao_contas.associacao.uuid,
                                                  periodo=prestacao_contas.periodo,
                                                  conta=prestacao_contas.conta_associacao)
    info = {
        'uuid': prestacao_contas.uuid,
        'acoes': info_acoes,
        'totais': totaliza_info_acoes(info_acoes),
    }
    return info


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


def receitas_conciliadas_por_conta_e_acao_na_prestacao_contas(conta_associacao, acao_associacao, prestacao_contas):
    dataset = prestacao_contas.receitas_conciliadas.filter(conta_associacao=conta_associacao).filter(
        acao_associacao=acao_associacao)

    return dataset.all()


def despesas_nao_conciliadas_por_conta_e_acao_no_periodo(conta_associacao, acao_associacao, periodo):
    dataset = RateioDespesa.objects.filter(conta_associacao=conta_associacao).filter(
        acao_associacao=acao_associacao).filter(conferido=False)

    # No caso de despesas não conciliadas todas devem ser exibidas até a data limite do período
    if periodo.data_fim_realizacao_despesas:
        dataset = dataset.filter(despesa__data_documento__lte=periodo.data_fim_realizacao_despesas)

    return dataset.all()


def despesas_conciliadas_por_conta_e_acao_na_prestacao_contas(conta_associacao, acao_associacao, prestacao_contas):
    dataset = prestacao_contas.despesas_conciliadas.filter(conta_associacao=conta_associacao).filter(
        acao_associacao=acao_associacao)

    return dataset.all()


def info_conciliacao_acao_associacao_no_periodo(acao_associacao, prestacao_contas):
    def resultado_vazio():
        return {
            'receitas_no_periodo': 0,
            'despesas_no_periodo': 0,
            'receitas_nao_conciliadas': 0,
            'despesas_nao_conciliadas': 0,
        }

    def sumariza_conciliacao_receitas_do_periodo_e_acao(prestacao_contas, acao_associacao, info):

        receitas_conciliadas = receitas_conciliadas_por_conta_e_acao_na_prestacao_contas(
            conta_associacao=prestacao_contas.conta_associacao,
            acao_associacao=acao_associacao,
            prestacao_contas=prestacao_contas)

        for receita_conciliada in receitas_conciliadas:
            info['receitas_no_periodo'] += receita_conciliada.valor

        receitas_nao_conciliadas = receitas_nao_conciliadas_por_conta_e_acao_no_periodo(
            conta_associacao=prestacao_contas.conta_associacao,
            acao_associacao=acao_associacao,
            periodo=prestacao_contas.periodo)

        for receita_nao_conciliada in receitas_nao_conciliadas:
            info['receitas_no_periodo'] += receita_nao_conciliada.valor
            info['receitas_nao_conciliadas'] += receita_nao_conciliada.valor

        return info

    def sumariza_conciliacao_despesas_do_periodo_e_acao(prestacao_contas, acao_associacao, info, ):
        rateios_conciliados = despesas_conciliadas_por_conta_e_acao_na_prestacao_contas(
            conta_associacao=prestacao_contas.conta_associacao,
            acao_associacao=acao_associacao,
            prestacao_contas=prestacao_contas)

        for rateio_conciliado in rateios_conciliados:
            info['despesas_no_periodo'] += rateio_conciliado.valor_rateio

        rateios_nao_conciliados = despesas_nao_conciliadas_por_conta_e_acao_no_periodo(
            conta_associacao=prestacao_contas.conta_associacao,
            acao_associacao=acao_associacao,
            periodo=prestacao_contas.periodo)

        for rateio_nao_conciliado in rateios_nao_conciliados:
            info['despesas_no_periodo'] += rateio_nao_conciliado.valor_rateio
            info['despesas_nao_conciliadas'] += rateio_nao_conciliado.valor_rateio

        return info

    info = resultado_vazio()

    info = sumariza_conciliacao_receitas_do_periodo_e_acao(prestacao_contas=prestacao_contas,
                                                           acao_associacao=acao_associacao,
                                                           info=info)

    info = sumariza_conciliacao_despesas_do_periodo_e_acao(prestacao_contas=prestacao_contas,
                                                           acao_associacao=acao_associacao, info=info)

    return info


def info_conciliacao_pendente(prestacao_contas):
    acoes_associacao = Associacao.acoes_da_associacao(associacao_uuid=prestacao_contas.associacao.uuid)
    result = []
    for acao_associacao in acoes_associacao:
        info_acao = info_conciliacao_acao_associacao_no_periodo(acao_associacao=acao_associacao,
                                                                prestacao_contas=prestacao_contas)

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
