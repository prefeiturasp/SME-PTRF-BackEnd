import pytest

from ...models import Receita

pytestmark = pytest.mark.django_db


def test_resultado_periodo_com_receitas(
    periodo_2020_1,
    acao_associacao_role_cultural,
    receita_2019_2_role_repasse_capital_conferida,
    receita_2020_1_role_repasse_capital_conferida,
    receita_2020_1_role_repasse_capital_nao_conferida,
    receita_2020_1_role_rendimento_custeio_conferida,
    receita_2020_1_role_repasse_custeio_conferida,
    receita_2020_1_ptrf_repasse_capital_conferida,
):
    resultado = Receita.totais_por_acao_associacao_no_periodo(acao_associacao_role_cultural, periodo_2020_1)

    total_receitas_capital_esperado = receita_2020_1_role_repasse_capital_conferida.valor + \
                                      receita_2020_1_role_repasse_capital_nao_conferida.valor

    total_repasses_capital_esperado = receita_2020_1_role_repasse_capital_conferida.valor + \
                                      receita_2020_1_role_repasse_capital_nao_conferida.valor

    total_receitas_custeio_esperado = receita_2020_1_role_rendimento_custeio_conferida.valor + \
                                      receita_2020_1_role_repasse_custeio_conferida.valor

    total_repasses_custeio_esperado = receita_2020_1_role_repasse_custeio_conferida.valor

    esperados = [
        ('total_receitas_capital', total_receitas_capital_esperado),
        ('total_repasses_capital', total_repasses_capital_esperado),
        ('total_receitas_custeio', total_receitas_custeio_esperado),
        ('total_repasses_custeio', total_repasses_custeio_esperado),
    ]

    for esperado in esperados:
        assert resultado[esperado[0]] == esperado[1], f"{esperado[0]} diferente do esperado."
