from datetime import date
import pytest
from rest_framework import status
from model_bakery import baker

pytestmark = pytest.mark.django_db


@pytest.fixture
def periodo_anterior_teste_acompanahmento_de_relatorios_consolidados():
    return baker.make(
        'Periodo',
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 6, 16),
        data_fim_realizacao_despesas=date(2021, 12, 31),
    )


@pytest.fixture
def periodo_teste_acompanahmento_de_relatorios_consolidados(
    periodo_anterior_teste_acompanahmento_de_relatorios_consolidados
):
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
        periodo_anterior=periodo_anterior_teste_acompanahmento_de_relatorios_consolidados,
    )


def test_action_listagem_de_relatorios_consolidados_sme_por_status(
    jwt_authenticated_client_dre,
    periodo_teste_acompanahmento_de_relatorios_consolidados
):
    periodo_uuid = periodo_teste_acompanahmento_de_relatorios_consolidados.uuid

    response = jwt_authenticated_client_dre.get(
        f'/api/consolidados-dre/listagem-de-relatorios-consolidados-sme-por-status/?periodo={periodo_uuid}',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


def test_action_listagem_de_relatorios_consolidados_sme_por_status_periodo_errado(
    jwt_authenticated_client_dre,
    periodo_teste_acompanahmento_de_relatorios_consolidados
):
    periodo_uuid = periodo_teste_acompanahmento_de_relatorios_consolidados.uuid

    response = jwt_authenticated_client_dre.get(
        f'/api/consolidados-dre/listagem-de-relatorios-consolidados-sme-por-status/?periodo={periodo_uuid}XXX',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_action_listagem_de_relatorios_consolidados_sme_por_status_sem_periodo(
    jwt_authenticated_client_dre,
):

    response = jwt_authenticated_client_dre.get(
        f'/api/consolidados-dre/listagem-de-relatorios-consolidados-sme-por-status/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
