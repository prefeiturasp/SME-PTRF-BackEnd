import pytest
from decimal import Decimal
from sme_ptrf_apps.core.services.dados_demo_financeiro_service import cria_resumo_por_acao

pytestmark = pytest.mark.django_db


def test_resumo_por_acao_sem_movimento(
    associacao,
    df_conta_associacao_cartao,
    df_periodo_2020_1,
):
    esperado = {
        'resumo_acoes': [],
        'total_conciliacao': 0,
        'total_valores': {
            'credito': {'C': 0, 'K': 0, 'L': 0},
            'credito_nao_demonstrado': {'C': 0, 'K': 0, 'L': 0},
            'despesa_nao_demostrada_outros_periodos': {'C': 0, 'K': 0, 'L': 0},
            'despesa_nao_realizada': {'C': 0, 'K': 0, 'L': 0},
            'despesa_realizada': {'C': 0, 'K': 0, 'L': 0},
            'saldo_anterior': {'C': 0, 'K': 0, 'L': 0},
            'saldo_bancario': 0,
            'saldo_reprogramado_proximo': {'C': 0, 'K': 0, 'L': 0},
            'total_valores': 0,
            'valor_saldo_bancario': {'C': 0, 'K': 0, 'L': 0},
            'valor_saldo_reprogramado_proximo_periodo': {'C': 0, 'K': 0, 'L': 0}
        }
    }

    acoes = associacao.acoes.filter(status='ATIVA')
    resultado = cria_resumo_por_acao(acoes, df_conta_associacao_cartao, df_periodo_2020_1)
    assert resultado == esperado


def test_resumo_por_acao_com_despesa_conciliada_no_periodo(
    associacao,
    df_conta_associacao_cartao,
    df_periodo_2020_1,
    df_receita_2020_1_cartao_ptrf_repasse_custeio_conferida_em_2020_1,
    df_rateio_despesa_2020_1_cartao_ptrf_custeio_conferido_em_2020_1
):
    esperado = {
        'resumo_acoes': [
            {
                'acao_associacao': 'PTRF',
                'linha_capital': {
                    'credito': 0,
                    'credito_nao_demonstrado': 0,
                    'despesa_nao_demostrada_outros_periodos': 0,
                    'despesa_nao_realizada': 0,
                    'despesa_realizada': 0,
                    'saldo_anterior': 0,
                    'saldo_bancario': 0,
                    'saldo_reprogramado_proximo': 0,
                    'saldo_reprogramado_proximo_vr': 0,
                    'valor_saldo_bancario_capital': 0,
                    'valor_saldo_reprogramado_proximo_periodo_capital': 0
                },
                'linha_custeio': {
                    'credito': Decimal('100.00'),
                    'credito_nao_demonstrado': 0,
                    'despesa_nao_demostrada_outros_periodos': 0,
                    'despesa_nao_realizada': 0,
                    'despesa_realizada': Decimal('100.00'),
                    'saldo_anterior': 0,
                    'saldo_bancario': 0,
                    'saldo_reprogramado_proximo': 0,
                    'saldo_reprogramado_proximo_vr': 0,
                    'valor_saldo_bancario_custeio': 0,
                    'valor_saldo_reprogramado_proximo_periodo_custeio': 0
                },
                'linha_livre': {
                    'credito': 0,
                    'credito_nao_demonstrado': 0,
                    'saldo_anterior': 0,
                    'saldo_reprogramado_proximo': 0,
                    'saldo_reprogramado_proximo_vr': 0,
                    'valor_saldo_reprogramado_proximo_periodo_livre': 0
                },
                'saldo_bancario': 0,
                'total_conciliacao': 0,
                'total_valores': 0
            }
        ],
        'total_conciliacao': 0,
        'total_valores': {
            'credito': {'C': Decimal('100.00'), 'K': 0, 'L': 0},
            'credito_nao_demonstrado': {'C': 0, 'K': 0, 'L': 0},
            'despesa_nao_demostrada_outros_periodos': {'C': 0, 'K': 0, 'L': 0},
            'despesa_nao_realizada': {'C': 0, 'K': 0, 'L': 0},
            'despesa_realizada': {'C': Decimal('100.00'), 'K': 0, 'L': 0},
            'saldo_anterior': {'C': 0, 'K': 0, 'L': 0},
            'saldo_bancario': 0,
            'saldo_reprogramado_proximo': {'C': 0, 'K': 0, 'L': 0},
            'total_valores': 0,
            'valor_saldo_bancario': {'C': 0, 'K': 0, 'L': 0},
            'valor_saldo_reprogramado_proximo_periodo': {'C': 0, 'K': 0, 'L': 0}
        }
    }

    acoes = associacao.acoes.filter(status='ATIVA')
    resultado = cria_resumo_por_acao(acoes, df_conta_associacao_cartao, df_periodo_2020_1)
    assert resultado == esperado


def test_resumo_por_acao_com_despesa_conciliada_em_periodo_futuro(
    associacao,
    df_conta_associacao_cartao,
    df_periodo_2020_1,
    df_receita_2020_1_cartao_ptrf_repasse_custeio_conferida_em_2020_1,
    df_rateio_despesa_2020_1_cartao_ptrf_custeio_conferido_em_2020_2
):
    acoes = associacao.acoes.filter(status='ATIVA')
    resultado = cria_resumo_por_acao(acoes, df_conta_associacao_cartao, df_periodo_2020_1)

    assert resultado['resumo_acoes'][0]['linha_custeio']['despesa_nao_realizada'] == Decimal('100.00')
    assert resultado['resumo_acoes'][0]['linha_custeio']['despesa_realizada'] == 0


def test_resumo_por_acao_com_despesa_nao_conciliada_de_periodos_anteriores(
    associacao,
    df_conta_associacao_cartao,
    df_periodo_2020_1,
    df_receita_2020_1_cartao_ptrf_repasse_custeio_conferida_em_2020_1,
    df_rateio_despesa_2019_2_cartao_ptrf_custeio_nao_conferido
):
    acoes = associacao.acoes.filter(status='ATIVA')
    resultado = cria_resumo_por_acao(acoes, df_conta_associacao_cartao, df_periodo_2020_1)

    assert resultado['resumo_acoes'][0]['linha_custeio']['despesa_nao_realizada'] == 0
    assert resultado['resumo_acoes'][0]['linha_custeio']['despesa_nao_demostrada_outros_periodos'] == Decimal('100.00')
    assert resultado['resumo_acoes'][0]['linha_custeio']['despesa_realizada'] == 0


def test_resumo_por_acao_com_despesa_nao_conciliada_de_periodos_anteriores_conciliacao_em_periodo_futuro(
    associacao,
    df_conta_associacao_cartao,
    df_periodo_2020_1,
    df_receita_2020_1_cartao_ptrf_repasse_custeio_conferida_em_2020_1,
    df_rateio_despesa_2019_2_cartao_ptrf_custeio_conferido_em_2020_2
):
    acoes = associacao.acoes.filter(status='ATIVA')
    resultado = cria_resumo_por_acao(acoes, df_conta_associacao_cartao, df_periodo_2020_1)

    assert resultado['resumo_acoes'][0]['linha_custeio']['despesa_nao_realizada'] == 0
    assert resultado['resumo_acoes'][0]['linha_custeio']['despesa_nao_demostrada_outros_periodos'] == Decimal('100.00')
    assert resultado['resumo_acoes'][0]['linha_custeio']['despesa_realizada'] == 0

