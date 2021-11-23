import pytest
from model_bakery import baker
from decimal import Decimal

from ....services import info_acoes_associacao_no_periodo
from .....core.models import STATUS_FECHADO

pytestmark = pytest.mark.django_db


@pytest.fixture
def fechamento_periodo_ptrf(periodo_2020_1, associacao, conta_associacao_cheque, acao_associacao_ptrf, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao_cheque,
        acao_associacao=acao_associacao_ptrf,
        fechamento_anterior=None,
        total_receitas_capital=10000,
        total_repasses_capital=5000,
        total_despesas_capital=1000,
        total_receitas_custeio=20000,
        total_repasses_custeio=10000,
        total_despesas_custeio=2000,
        total_receitas_livre=30000,
        total_repasses_livre=15000,
        status=STATUS_FECHADO
        # O saldo reprogramado deve ser: Cap:10000-1000=9000 + Cus:20000-2000=18000 + Liv:30000 = 57000
    )


def test_resultado_periodo_fechado(
    fechamento_periodo_ptrf,
):
    resultado_esperado = [
        {
            'acao_associacao_uuid': f'{fechamento_periodo_ptrf.acao_associacao.uuid}',
            'acao_associacao_nome': fechamento_periodo_ptrf.acao_associacao.acao.nome,

            'saldo_reprogramado': 0,
            'saldo_reprogramado_capital': 0,
            'saldo_reprogramado_custeio': 0,
            'saldo_reprogramado_livre': 0,

            'receitas_no_periodo': Decimal('60000.00'),

            'receitas_devolucao_no_periodo': Decimal('0.00'),
            'receitas_devolucao_no_periodo_capital': Decimal('0.00'),
            'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
            'receitas_devolucao_no_periodo_livre': Decimal('0.00'),

            'repasses_no_periodo': Decimal('30000.00'),
            'repasses_no_periodo_capital': Decimal('5000.00'),
            'repasses_no_periodo_custeio': Decimal('10000.00'),
            'repasses_no_periodo_livre': Decimal('15000.00'),

            'outras_receitas_no_periodo': Decimal('30000.00'),
            'outras_receitas_no_periodo_capital': Decimal('5000.00'),
            'outras_receitas_no_periodo_custeio': Decimal('10000.00'),
            'outras_receitas_no_periodo_livre': Decimal('15000.00'),

            'despesas_no_periodo': Decimal('3000.00'),
            'despesas_no_periodo_capital': Decimal('1000.00'),
            'despesas_no_periodo_custeio': Decimal('2000.00'),

            'despesas_nao_conciliadas': Decimal('0.00'),
            'despesas_nao_conciliadas_capital': Decimal('0.00'),
            'despesas_nao_conciliadas_custeio': Decimal('0.00'),

            'receitas_nao_conciliadas': Decimal('0.00'),
            'receitas_nao_conciliadas_capital': Decimal('0.00'),
            'receitas_nao_conciliadas_custeio': Decimal('0.00'),
            'receitas_nao_conciliadas_livre': Decimal('0.00'),

            'saldo_atual_capital': Decimal('9000.00'),
            'saldo_atual_custeio': Decimal('18000.00'),
            'saldo_atual_livre': Decimal('30000.00'),
            'saldo_atual_total': Decimal('57000.00'),

            'especificacoes_despesas_capital': [],
            'especificacoes_despesas_custeio': [],

            'repasses_nao_realizados_capital': 0,
            'repasses_nao_realizados_custeio': 0,
            'repasses_nao_realizados_livre': 0,

            'despesas_conciliadas': Decimal('3000.00'),
            'despesas_conciliadas_capital': Decimal('1000.00'),
            'despesas_conciliadas_custeio': Decimal('2000.00'),

            'despesas_nao_conciliadas_anteriores': 0,
            'despesas_nao_conciliadas_anteriores_capital': 0,
            'despesas_nao_conciliadas_anteriores_custeio': 0,

            'saldo_bancario_capital': Decimal('9000.00'),
            'saldo_bancario_custeio': Decimal('18000.00'),
            'saldo_bancario_livre': Decimal('30000.00'),
            'saldo_bancario_total': Decimal('57000.00'),

        },
    ]
    resultado = info_acoes_associacao_no_periodo(fechamento_periodo_ptrf.associacao.uuid,
                                                 fechamento_periodo_ptrf.periodo)

    assert resultado == resultado_esperado

#
# def test_resultado_periodo_aberto_sem_receitas_sem_despesas(
#     periodo,
#     acao_associacao,
#     fechamento_periodo_anterior
# ):
#     resultado_esperado = {
#         'saldo_anterior_custeio': 200,
#         'receitas_no_periodo_custeio': 0,
#         'repasses_no_periodo_custeio': 0,
#         'despesas_no_periodo_custeio': 0,
#         'saldo_atual_custeio': 200,
#         'despesas_nao_conciliadas_custeio': 0.0,
#         'receitas_nao_conciliadas_custeio': 0.0,
#
#         'saldo_anterior_capital': 100,
#         'receitas_no_periodo_capital': 0,
#         'repasses_no_periodo_capital': 0,
#         'despesas_no_periodo_capital': 0,
#         'saldo_atual_capital': 100,
#         'despesas_nao_conciliadas_capital': 0.0,
#         'receitas_nao_conciliadas_capital': 0.0,
#
#         'saldo_anterior_livre': 2000,
#         'receitas_no_periodo_livre': 0,
#         'repasses_no_periodo_livre': 0,
#         'saldo_atual_livre': 2000,
#         'receitas_nao_conciliadas_livre': 0.0,
#
#     }
#     resultado = info_acao_associacao_no_periodo(acao_associacao, periodo)
#
#     assert resultado == resultado_esperado
#
#
# def test_resultado_periodo_aberto_com_receitas_sem_despesas(
#     periodo,
#     acao_associacao,
#     fechamento_periodo_anterior,
#     receita_50_fora_do_periodo,
#     receita_100_no_periodo,
#     receita_200_no_inicio_do_periodo,
#     receita_300_no_fim_do_periodo,
#     receita_1000_no_periodo_livre_aplicacao
# ):
#     resultado_esperado = {
#         'saldo_anterior_custeio': 200,
#         'receitas_no_periodo_custeio': 600,
#         'repasses_no_periodo_custeio': 0,
#         'despesas_no_periodo_custeio': 0,
#         'saldo_atual_custeio': 800,
#         'despesas_nao_conciliadas_custeio': 0.0,
#         'receitas_nao_conciliadas_custeio': 600.0,
#
#         'saldo_anterior_capital': 100,
#         'receitas_no_periodo_capital': 0,
#         'repasses_no_periodo_capital': 0,
#         'despesas_no_periodo_capital': 0,
#         'saldo_atual_capital': 100,
#         'despesas_nao_conciliadas_capital': 0.0,
#         'receitas_nao_conciliadas_capital': 0.0,
#
#         'saldo_anterior_livre': 2000,
#         'receitas_no_periodo_livre': 1000,
#         'repasses_no_periodo_livre': 0,
#         'saldo_atual_livre': 3000,
#         'receitas_nao_conciliadas_livre': 1000.0,
#
#     }
#     resultado = info_acao_associacao_no_periodo(acao_associacao, periodo)
#
#     assert resultado == resultado_esperado
#
#
# def test_resultado_periodo_aberto_com_despesas_sem_receitas(
#     periodo,
#     acao_associacao,
#     fechamento_periodo_anterior,
#     despesa_no_periodo,
#     rateio_no_periodo_10_custeio_outra_acao,
#     rateio_no_periodo_200_capital,
#     rateio_no_periodo_100_custeio,
#     despesa_fora_periodo,
#     rateio_fora_periodo_50_custeio
# ):
#     resultado_esperado = {
#         'saldo_anterior_custeio': 200,
#         'receitas_no_periodo_custeio': 0,
#         'repasses_no_periodo_custeio': 0,
#         'despesas_no_periodo_custeio': 100,
#         'saldo_atual_custeio': 100,
#         'despesas_nao_conciliadas_custeio': 100.0,
#         'receitas_nao_conciliadas_custeio': 0.0,
#
#         'saldo_anterior_capital': 100,
#         'receitas_no_periodo_capital': 0,
#         'repasses_no_periodo_capital': 0,
#         'despesas_no_periodo_capital': 200,
#         'saldo_atual_capital': -100,
#         'despesas_nao_conciliadas_capital': 200.0,
#         'receitas_nao_conciliadas_capital': 0.0,
#
#         'saldo_anterior_livre': 2000,
#         'receitas_no_periodo_livre': 0,
#         'repasses_no_periodo_livre': 0,
#         'saldo_atual_livre': 2000,
#         'receitas_nao_conciliadas_livre': 0.0,
#
#     }
#     resultado = info_acao_associacao_no_periodo(acao_associacao, periodo)
#
#     assert resultado == resultado_esperado
#
#
# def test_resultado_periodo_aberto_com_despesas_e_receitas(
#     periodo,
#     acao_associacao,
#     fechamento_periodo_anterior,
#     despesa_no_periodo,
#     rateio_no_periodo_10_custeio_outra_acao,
#     rateio_no_periodo_200_capital,
#     rateio_no_periodo_100_custeio,
#     despesa_fora_periodo,
#     rateio_fora_periodo_50_custeio,
#     receita_50_fora_do_periodo,
#     receita_100_no_periodo,
#     receita_200_no_inicio_do_periodo,
#     receita_300_no_fim_do_periodo
# ):
#     resultado_esperado = {
#         'saldo_anterior_custeio': 200,
#         'receitas_no_periodo_custeio': 600,
#         'repasses_no_periodo_custeio': 0,
#         'despesas_no_periodo_custeio': 100,
#         'saldo_atual_custeio': 700,
#         'despesas_nao_conciliadas_custeio': 100.0,
#         'receitas_nao_conciliadas_custeio': 600.0,
#
#         'saldo_anterior_capital': 100,
#         'receitas_no_periodo_capital': 0,
#         'repasses_no_periodo_capital': 0,
#         'despesas_no_periodo_capital': 200,
#         'saldo_atual_capital': -100,
#         'despesas_nao_conciliadas_capital': 200.0,
#         'receitas_nao_conciliadas_capital': 0.0,
#
#         'saldo_anterior_livre': 2000,
#         'receitas_no_periodo_livre': 0,
#         'repasses_no_periodo_livre': 0,
#         'saldo_atual_livre': 2000,
#         'receitas_nao_conciliadas_livre': 0.0,
#
#     }
#     resultado = info_acao_associacao_no_periodo(acao_associacao, periodo)
#
#     assert resultado == resultado_esperado
