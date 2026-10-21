from decimal import Decimal

from sme_ptrf_apps.dre.services.dados_demo_execucao_fisico_financeira_service import (
    retorna_objeto_totais_todas_as_contas_execucao_financeira_vazio,
    retorna_total_todas_as_contas_execucao_financeira,
)


def test_total_devolucoes_ao_tesouro_nao_soma_novamente_valor_de_cada_tipo_conta():
    conta_cheque = retorna_objeto_totais_todas_as_contas_execucao_financeira_vazio()
    conta_cartao = retorna_objeto_totais_todas_as_contas_execucao_financeira_vazio()

    conta_cheque['livre']['devolucoes_ao_tesouro_no_periodo_total'] = '2.404,30'
    conta_cheque['totais']['devolucoes_ao_tesouro_no_periodo_total'] = '2.404,30'
    conta_cartao['livre']['devolucoes_ao_tesouro_no_periodo_total'] = '2.404,30'
    conta_cartao['totais']['devolucoes_ao_tesouro_no_periodo_total'] = '2.404,30'

    resultado = retorna_total_todas_as_contas_execucao_financeira(
        [conta_cheque, conta_cartao],
        total_devolucoes_ao_tesouro=Decimal('2404.30'),
    )

    assert resultado['totais']['devolucoes_ao_tesouro_no_periodo_total'] == '2.404,30'
