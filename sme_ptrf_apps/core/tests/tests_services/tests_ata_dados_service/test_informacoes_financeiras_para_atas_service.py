import pytest
from decimal import Decimal

from sme_ptrf_apps.core.services.ata_dados_service import informacoes_financeiras_para_atas

pytestmark = pytest.mark.django_db


def test_info_financeira_estrutura_resultado(
    ata_prestacao_conta_2020_1,
    ata_fechamento_periodo_2020_1,
    ata_conta_associacao_cartao,
    ata_acao_associacao_ptrf,
):
    esperado = {
        'contas': [
            {
                'acoes': [
                    {
                        'acao_associacao_nome': 'PTRF',
                        'acao_associacao_uuid': f'{ata_acao_associacao_ptrf.uuid}',
                        'despesas_conciliadas': Decimal('100.00'),
                        'despesas_conciliadas_capital': Decimal('0.00'),
                        'despesas_conciliadas_custeio': Decimal('100.00'),
                        'despesas_nao_conciliadas': Decimal('0.00'),
                        'despesas_nao_conciliadas_anteriores': 0,
                        'despesas_nao_conciliadas_anteriores_capital': 0,
                        'despesas_nao_conciliadas_anteriores_custeio': 0,
                        'despesas_nao_conciliadas_capital': Decimal('0.00'),
                        'despesas_nao_conciliadas_custeio': Decimal('0.00'),
                        'despesas_no_periodo': Decimal('100.00'),
                        'despesas_no_periodo_capital': Decimal('0.00'),
                        'despesas_no_periodo_custeio': Decimal('100.00'),
                        'especificacoes_despesas_capital': [],
                        'especificacoes_despesas_custeio': [],
                        'outras_receitas_no_periodo': Decimal('0.00'),
                        'outras_receitas_no_periodo_capital': Decimal('0.00'),
                        'outras_receitas_no_periodo_custeio': Decimal('0.00'),
                        'outras_receitas_no_periodo_livre': Decimal('0.00'),
                        'receitas_devolucao_no_periodo': Decimal('0.00'),
                        'receitas_devolucao_no_periodo_capital': Decimal('0.00'),
                        'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
                        'receitas_devolucao_no_periodo_livre': Decimal('0.00'),
                        'receitas_nao_conciliadas': Decimal('0.00'),
                        'receitas_nao_conciliadas_capital': Decimal('0.00'),
                        'receitas_nao_conciliadas_custeio': Decimal('0.00'),
                        'receitas_nao_conciliadas_livre': Decimal('0.00'),
                        'receitas_no_periodo': Decimal('100.00'),
                        'repasses_nao_realizados_capital': 0,
                        'repasses_nao_realizados_custeio': 0,
                        'repasses_nao_realizados_livre': 0,
                        'repasses_no_periodo': Decimal('100.00'),
                        'repasses_no_periodo_capital': Decimal('0.00'),
                        'repasses_no_periodo_custeio': Decimal('100.00'),
                        'repasses_no_periodo_livre': Decimal('0.00'),
                        'saldo_atual_capital': Decimal('0.00'),
                        'saldo_atual_custeio': Decimal('0.00'),
                        'saldo_atual_livre': Decimal('0.00'),
                        'saldo_atual_total': Decimal('0.00'),
                        'saldo_bancario_capital': Decimal('0.00'),
                        'saldo_bancario_custeio': Decimal('0.00'),
                        'saldo_bancario_livre': Decimal('0.00'),
                        'saldo_bancario_total': Decimal('0.00'),
                        'saldo_reprogramado': 0,
                        'saldo_reprogramado_capital': 0,
                        'saldo_reprogramado_custeio': 0,
                        'saldo_reprogramado_livre': 0
                    }
                ],
                'conta_associacao': {
                    'agencia': '',
                    'banco_nome': '',
                    'nome': 'Cartão',
                    'numero_conta': '',
                    'uuid': f'{ata_conta_associacao_cartao.uuid}'
                },
                'totais': {
                    'despesas_conciliadas': Decimal('100.00'),
                    'despesas_conciliadas_capital': Decimal('0.00'),
                    'despesas_conciliadas_custeio': Decimal('100.00'),
                    'despesas_nao_conciliadas': Decimal('0.00'),
                    'despesas_nao_conciliadas_anteriores': 0,
                    'despesas_nao_conciliadas_anteriores_capital': 0,
                    'despesas_nao_conciliadas_anteriores_custeio': 0,
                    'despesas_nao_conciliadas_capital': Decimal('0.00'),
                    'despesas_nao_conciliadas_custeio': Decimal('0.00'),
                    'despesas_no_periodo': Decimal('100.00'),
                    'despesas_no_periodo_capital': Decimal('0.00'),
                    'despesas_no_periodo_custeio': Decimal('100.00'),
                    'outras_receitas_no_periodo': Decimal('0.00'),
                    'outras_receitas_no_periodo_capital': Decimal('0.00'),
                    'outras_receitas_no_periodo_custeio': Decimal('0.00'),
                    'outras_receitas_no_periodo_livre': Decimal('0.00'),
                    'receitas_devolucao_no_periodo': Decimal('0.00'),
                    'receitas_devolucao_no_periodo_capital': Decimal('0.00'),
                    'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
                    'receitas_devolucao_no_periodo_livre': Decimal('0.00'),
                    'receitas_nao_conciliadas': Decimal('0.00'),
                    'receitas_nao_conciliadas_capital': Decimal('0.00'),
                    'receitas_nao_conciliadas_custeio': Decimal('0.00'),
                    'receitas_nao_conciliadas_livre': Decimal('0.00'),
                    'receitas_no_periodo': Decimal('100.00'),
                    'repasses_nao_realizados_capital': 0,
                    'repasses_nao_realizados_custeio': 0,
                    'repasses_nao_realizados_livre': 0,
                    'repasses_no_periodo': Decimal('100.00'),
                    'repasses_no_periodo_capital': Decimal('0.00'),
                    'repasses_no_periodo_custeio': Decimal('100.00'),
                    'repasses_no_periodo_livre': Decimal('0.00'),
                    'saldo_atual_capital': Decimal('0.00'),
                    'saldo_atual_custeio': Decimal('0.00'),
                    'saldo_atual_livre': Decimal('0.00'),
                    'saldo_atual_total': Decimal('0.00'),
                    'saldo_bancario_capital': Decimal('0.00'),
                    'saldo_bancario_custeio': Decimal('0.00'),
                    'saldo_bancario_livre': Decimal('0.00'),
                    'saldo_bancario_total': Decimal('0.00'),
                    'saldo_reprogramado': 0,
                    'saldo_reprogramado_capital': 0,
                    'saldo_reprogramado_custeio': 0,
                    'saldo_reprogramado_livre': 0
                }
            }
        ],
    }

    resultado = informacoes_financeiras_para_atas(ata_prestacao_conta_2020_1)
    resultado.pop('uuid')
    assert resultado == esperado


def test_info_financeira_estrutura_despesa_anterior_nao_conferida(
    ata_prestacao_conta_2020_1,
    ata_fechamento_periodo_2020_1,
    ata_conta_associacao_cartao,
    ata_acao_associacao_ptrf,
    ata_rateio_despesa_2019_2_cartao_ptrf_custeio_nao_conferido
):
    resultado = informacoes_financeiras_para_atas(ata_prestacao_conta_2020_1)
    assert resultado['contas'][0]['acoes'][0]['despesas_nao_conciliadas_anteriores'] == Decimal('100.00')
    assert resultado['contas'][0]['acoes'][0]['despesas_nao_conciliadas_anteriores_custeio'] == Decimal('100.00')
    assert resultado['contas'][0]['totais']['despesas_nao_conciliadas_anteriores'] == Decimal('100.00')
    assert resultado['contas'][0]['totais']['despesas_nao_conciliadas_anteriores_custeio'] == Decimal('100.00')


def test_info_financeira_estrutura_despesa_anterior_conferida_no_futuro(
    ata_prestacao_conta_2020_1,
    ata_fechamento_periodo_2020_1,
    ata_conta_associacao_cartao,
    ata_acao_associacao_ptrf,
    ata_rateio_despesa_2019_2_cartao_ptrf_custeio_conferido_em_2020_2
):
    resultado = informacoes_financeiras_para_atas(ata_prestacao_conta_2020_1)
    assert resultado['contas'][0]['acoes'][0]['despesas_nao_conciliadas_anteriores'] == Decimal('100.00')
    assert resultado['contas'][0]['acoes'][0]['despesas_nao_conciliadas_anteriores_custeio'] == Decimal('100.00')
    assert resultado['contas'][0]['totais']['despesas_nao_conciliadas_anteriores'] == Decimal('100.00')
    assert resultado['contas'][0]['totais']['despesas_nao_conciliadas_anteriores_custeio'] == Decimal('100.00')
