import pytest
from model_bakery import baker
from datetime import date


pytestmark = pytest.mark.django_db


@pytest.fixture
def conta_associacao_com_data_inicio_periodo_2019_2(associacao, tipo_conta_cheque):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta_cheque,
        data_inicio=date(2019, 9, 1)
    )


@pytest.fixture
def conta_associacao_com_data_inicio_periodo_2019_1(associacao, tipo_conta_cheque):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta_cheque,
        data_inicio=date(2019, 1, 1)
    )


@pytest.fixture
def conta_associacao_com_data_inicio_periodo_2020_1(associacao, tipo_conta_cheque):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta_cheque,
        data_inicio=date(2020, 1, 1)
    )


def test_conta_criada_no_periodo(
    conta_associacao_com_data_inicio_periodo_2019_2,
    periodo
):
    result = conta_associacao_com_data_inicio_periodo_2019_2.conta_criada_no_periodo_ou_periodo_anteriores(periodo)

    assert result is True


def test_conta_criada_no_periodo_anterior(
    conta_associacao_com_data_inicio_periodo_2019_1,
    periodo
):
    result = conta_associacao_com_data_inicio_periodo_2019_1.conta_criada_no_periodo_ou_periodo_anteriores(periodo)

    assert result is True


def test_conta_criada_no_periodo_posterior(
    conta_associacao_com_data_inicio_periodo_2020_1,
    periodo
):
    # Essa conta foi criada no periodo posterior ao periodo informado
    result = conta_associacao_com_data_inicio_periodo_2020_1.conta_criada_no_periodo_ou_periodo_anteriores(periodo)

    assert result is False
