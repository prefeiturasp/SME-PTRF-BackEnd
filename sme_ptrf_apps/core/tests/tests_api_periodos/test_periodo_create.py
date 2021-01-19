import json
import pytest

from rest_framework import status


from sme_ptrf_apps.core.models import Periodo

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_periodo(periodo_2021_2):
    payload = {
        'referencia': '2021.3',
        'data_inicio_realizacao_despesas': '2021-07-01',
        'data_fim_realizacao_despesas': '2021-09-30',
        'data_prevista_repasse': '2021-07-01',
        'data_inicio_prestacao_contas': '2021-10-01',
        'data_fim_prestacao_contas': '2021-10-15',
        'periodo_anterior': f'{periodo_2021_2.uuid}'
    }
    return payload


@pytest.fixture
def payload_periodo_anterior_nulo(periodo_2021_2):
    payload = {
        'referencia': '2021.3',
        'data_inicio_realizacao_despesas': '2021-07-01',
        'data_fim_realizacao_despesas': '2021-09-30',
        'data_prevista_repasse': '2021-07-01',
        'data_inicio_prestacao_contas': '2021-10-01',
        'data_fim_prestacao_contas': '2021-10-15',
        'periodo_anterior': None
    }
    return payload


def test_create_periodo(
    jwt_authenticated_client_a,
    periodo_2021_2,
    payload_periodo
):
    response = jwt_authenticated_client_a.post(
        '/api/periodos/', data=json.dumps(payload_periodo), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Periodo.objects.filter(uuid=result['uuid']).exists()


def test_create_periodo_anterior_nulo(
    jwt_authenticated_client_a,
    periodo_2021_2,
    payload_periodo_anterior_nulo
):
    response = jwt_authenticated_client_a.post(
        '/api/periodos/', data=json.dumps(payload_periodo_anterior_nulo), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED, "Deve ser possível um periodo anterior nulo."

