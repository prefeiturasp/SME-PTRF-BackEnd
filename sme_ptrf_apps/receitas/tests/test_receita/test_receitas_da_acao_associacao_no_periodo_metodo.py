import pytest

from ...models import Receita

pytestmark = pytest.mark.django_db


def test_resultado_periodo_com_receitas(
    periodo,
    acao_associacao,
    receita_50_fora_do_periodo,
    receita_100_no_periodo,
    receita_200_no_inicio_do_periodo,
    receita_300_no_fim_do_periodo,
    receita_30_no_periodo_outra_acao
):
    resultado = Receita.receitas_da_acao_associacao_no_periodo(acao_associacao, periodo)

    assert len(resultado) == 3


def test_resultado_periodo_com_receitas_periodo_aberto(
    periodo_aberto,
    acao_associacao,
    receita_50_fora_do_periodo,
    receita_100_no_periodo,
    receita_200_no_inicio_do_periodo,
    receita_300_no_fim_do_periodo,
    receita_30_no_periodo_outra_acao
):
    resultado = Receita.receitas_da_acao_associacao_no_periodo(acao_associacao, periodo_aberto)

    assert len(resultado) == 3
