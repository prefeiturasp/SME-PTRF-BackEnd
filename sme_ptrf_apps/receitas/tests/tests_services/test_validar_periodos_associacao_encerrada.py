import pytest

pytestmark = pytest.mark.django_db


def test_periodos_validos_com_sem_associacao_encerrada(
    associacao_sem_data_de_encerramento_teste_periodo,
    periodo_anterior_teste_periodo,
    periodo_2020_teste_periodo,
    periodo_2021_teste_periodo,
    periodo_2022_teste_periodo,
):
    from ...services.receita_service import ValidaPeriodosReceitaAssociacaoEncerrada

    qs = ValidaPeriodosReceitaAssociacaoEncerrada(associacao=associacao_sem_data_de_encerramento_teste_periodo).response

    # Deve trazer 03 periodos periodo_2020_teste_periodo, periodo_2021_teste_periodo, periodo_2022_teste_periodo
    # Como não associacao não tem data de encerramento só não traz o proprio periodo inicial da associacao = periodo_anterior_teste_periodo

    assert qs.count() == 3


def test_periodos_validos_com_sem_associacao_encerrada_em_02_01_2020(
    associacao_com_data_de_encerramento_teste_periodo_02_01_2020,
    periodo_anterior_teste_periodo,
    periodo_2020_teste_periodo,
    periodo_2021_teste_periodo,
    periodo_2022_teste_periodo,
):
    from ...services.receita_service import ValidaPeriodosReceitaAssociacaoEncerrada

    qs = ValidaPeriodosReceitaAssociacaoEncerrada(associacao=associacao_com_data_de_encerramento_teste_periodo_02_01_2020).response

    # Deve trazer 01 periodo periodo_2020_teste_periodo.
    # Data de encerramento é 02/01/2020
    # Data data_inicio_realizacao_despesas é 01/01/2020

    assert qs.count() == 1

    assert qs[0].referencia == '2020.1'
