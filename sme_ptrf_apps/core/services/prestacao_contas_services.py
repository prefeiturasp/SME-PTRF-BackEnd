import logging

from ..models import PrestacaoConta
from ..services import info_acoes_associacao_no_periodo

logger = logging.getLogger(__name__)


def iniciar_prestacao_de_contas(periodo, associacao):
    return PrestacaoConta.iniciar(periodo=periodo, associacao=associacao)


def concluir_prestacao_de_contas(prestacao_contas_uuid):
    prestacao = PrestacaoConta.concluir(uuid=prestacao_contas_uuid)
    #TODO Rever serviço Concluir Prestação de Contas
    #
    # associacao = prestacao.associacao
    # periodo = prestacao.periodo
    # acoes = associacao.acoes.filter(status=AcaoAssociacao.STATUS_ATIVA)
    # conta = prestacao.conta_associacao
    #
    # for acao in acoes:
    #     totais_receitas = Receita.totais_por_acao_associacao_no_periodo(acao_associacao=acao, periodo=periodo, conta=conta)
    #     totais_despesas = RateioDespesa.totais_por_acao_associacao_no_periodo(acao_associacao=acao, periodo=periodo, conta=conta)
    #     especificacoes_despesas = RateioDespesa.especificacoes_dos_rateios_da_acao_associacao_no_periodo(
    #         acao_associacao=acao, periodo=periodo)
    #     FechamentoPeriodo.criar(
    #         prestacao_conta=prestacao,
    #         acao_associacao=acao,
    #         total_receitas_capital=totais_receitas['total_receitas_capital'],
    #         total_receitas_devolucao_capital=totais_receitas['total_receitas_devolucao_capital'],
    #         total_repasses_capital=totais_receitas['total_repasses_capital'],
    #         total_receitas_custeio=totais_receitas['total_receitas_custeio'],
    #         total_receitas_devolucao_custeio=totais_receitas['total_receitas_devolucao_custeio'],
    #         total_receitas_devolucao_livre=totais_receitas['total_receitas_devolucao_livre'],
    #         total_repasses_custeio=totais_receitas['total_repasses_custeio'],
    #         total_despesas_capital=totais_despesas['total_despesas_capital'],
    #         total_despesas_custeio=totais_despesas['total_despesas_custeio'],
    #         total_receitas_livre=totais_receitas['total_receitas_livre'],
    #         total_repasses_livre=totais_receitas['total_repasses_livre'],
    #         total_receitas_nao_conciliadas_capital=totais_receitas['total_receitas_nao_conciliadas_capital'],
    #         total_receitas_nao_conciliadas_custeio=totais_receitas['total_receitas_nao_conciliadas_custeio'],
    #         total_receitas_nao_conciliadas_livre=totais_receitas['total_receitas_nao_conciliadas_livre'],
    #         total_despesas_nao_conciliadas_capital=totais_despesas['total_despesas_nao_conciliadas_capital'],
    #         total_despesas_nao_conciliadas_custeio=totais_despesas['total_despesas_nao_conciliadas_custeio'],
    #         especificacoes_despesas=especificacoes_despesas
    #     )
    return prestacao


def reabrir_prestacao_de_contas(prestacao_contas_uuid):
    prestacao = PrestacaoConta.reabrir(uuid=prestacao_contas_uuid)

    return prestacao


def informacoes_financeiras_para_atas(prestacao_contas):
    def totaliza_info_acoes(info_acoes):
        totalizador = {
            'saldo_reprogramado': 0,
            'saldo_reprogramado_capital': 0,
            'saldo_reprogramado_custeio': 0,
            'saldo_reprogramado_livre': 0,

            'receitas_no_periodo': 0,

            'receitas_devolucao_no_periodo': 0,
            'receitas_devolucao_no_periodo_custeio': 0,
            'receitas_devolucao_no_periodo_capital': 0,
            'receitas_devolucao_no_periodo_livre': 0,

            'repasses_no_periodo': 0,
            'repasses_no_periodo_capital': 0,
            'repasses_no_periodo_custeio': 0,
            'repasses_no_periodo_livre': 0,

            'outras_receitas_no_periodo': 0,
            'outras_receitas_no_periodo_capital': 0,
            'outras_receitas_no_periodo_custeio': 0,
            'outras_receitas_no_periodo_livre': 0,

            'despesas_no_periodo': 0,
            'despesas_no_periodo_capital': 0,
            'despesas_no_periodo_custeio': 0,

            'despesas_nao_conciliadas': 0,
            'despesas_nao_conciliadas_capital': 0,
            'despesas_nao_conciliadas_custeio': 0,

            'receitas_nao_conciliadas': 0,
            'receitas_nao_conciliadas_capital': 0,
            'receitas_nao_conciliadas_custeio': 0,
            'receitas_nao_conciliadas_livre': 0,

            'saldo_atual_custeio': 0,
            'saldo_atual_capital': 0,
            'saldo_atual_livre': 0,
            'saldo_atual_total': 0,

            'repasses_nao_realizados_capital': 0,
            'repasses_nao_realizados_custeio': 0,
            'repasses_nao_realizados_livre': 0
        }
        for info_acao in info_acoes:
            for key in totalizador.keys():
                totalizador[key] += info_acao[key]

        return totalizador

    logger.debug(
        f'Get info financeiras para ata. Associacao:{prestacao_contas.associacao.uuid} Período:{prestacao_contas.periodo} Conta:{prestacao_contas.conta_associacao}')
    info_acoes = info_acoes_associacao_no_periodo(associacao_uuid=prestacao_contas.associacao.uuid,
                                                  periodo=prestacao_contas.periodo,
                                                  conta=prestacao_contas.conta_associacao)

    info_acoes = [info for info in info_acoes if info['saldo_reprogramado'] or info['receitas_no_periodo'] or info['despesas_no_periodo']]

    info = {
        'uuid': prestacao_contas.uuid,
        'acoes': info_acoes,
        'totais': totaliza_info_acoes(info_acoes),
    }
    return info
