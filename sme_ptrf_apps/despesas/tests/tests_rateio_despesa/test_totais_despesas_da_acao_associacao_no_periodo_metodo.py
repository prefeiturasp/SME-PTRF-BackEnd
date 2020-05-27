import pytest

from ...models import RateioDespesa

pytestmark = pytest.mark.django_db


def test_resultado_periodo_com_despesas(
    periodo_2020_1,
    acao_associacao_role_cultural,
    despesa_2020_1,
    rateio_despesa_2020_role_custeio_conferido,
    rateio_despesa_2020_role_custeio_nao_conferido,
    rateio_despesa_2020_role_capital_conferido,
    despesa_2019_2,
    rateio_despesa_2019_role_conferido,
):
    resultado = RateioDespesa.totais_por_acao_associacao_no_periodo(acao_associacao_role_cultural, periodo_2020_1)

    total_despesas_capital_esperado = rateio_despesa_2020_role_capital_conferido.valor_rateio

    total_despesas_custeio_esperado = rateio_despesa_2020_role_custeio_conferido.valor_rateio + \
                                      rateio_despesa_2020_role_custeio_nao_conferido.valor_rateio

    esperados = [
        ('total_despesas_capital', total_despesas_capital_esperado),
        ('total_despesas_custeio', total_despesas_custeio_esperado),
    ]

    for esperado in esperados:
        assert resultado[esperado[0]] == esperado[1], f"{esperado[0]} diferente do esperado."
