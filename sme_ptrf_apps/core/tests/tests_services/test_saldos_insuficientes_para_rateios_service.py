from decimal import Decimal

import pytest

from ...services import saldos_insuficientes_para_rateios
from ....despesas.models import RateioDespesa

pytestmark = pytest.mark.django_db

def test_resultado_saldos(
    fechamento_periodo_anterior,
    periodo_2020_1,
    acao,
    acao_associacao_role_cultural,
    despesa_2020_1,
    rateio_despesa_2020_role_custeio_conferido,
    rateio_despesa_2020_role_capital_conferido,
):
    resultado_esperado = [
        {
            'acao': rateio_despesa_2020_role_custeio_conferido.acao_associacao.acao.nome,
            'aplicacao': 'CUSTEIO',
            'saldo_disponivel': Decimal(-100.00),
            'total_rateios': rateio_despesa_2020_role_custeio_conferido.valor_rateio
        },
        {
            'acao': rateio_despesa_2020_role_capital_conferido.acao_associacao.acao.nome,
            'aplicacao': 'CAPITAL',
            'saldo_disponivel': Decimal(-100.00),
            'total_rateios': rateio_despesa_2020_role_capital_conferido.valor_rateio
        }
    ]

    rateios = RateioDespesa.objects.values()

    resultado = saldos_insuficientes_para_rateios(rateios=rateios, periodo=periodo_2020_1)

    assert resultado == resultado_esperado
