import pytest

from ...models import RateioDespesa

pytestmark = pytest.mark.django_db


def test_resultado_periodo_com_despesas(
    periodo,
    acao_associacao,
    despesa_no_periodo,
    rateio_no_periodo_100_custeio,
    rateio_no_periodo_200_capital,
    rateio_no_periodo_10_custeio_outra_acao,
    despesa_fora_periodo,
    rateio_fora_periodo_50_custeio
):
    resultado = RateioDespesa.rateios_da_acao_associacao_no_periodo(acao_associacao, periodo)

    assert len(resultado) == 2


def test_resultado_periodo_com_despesas_periodo_aberto(
    periodo_aberto,
    acao_associacao,
    despesa_no_periodo,
    rateio_no_periodo_100_custeio,
    rateio_no_periodo_200_capital,
    rateio_no_periodo_10_custeio_outra_acao,
    despesa_fora_periodo,
    rateio_fora_periodo_50_custeio
):
    resultado = RateioDespesa.rateios_da_acao_associacao_no_periodo(acao_associacao, periodo_aberto)

    assert len(resultado) == 2
