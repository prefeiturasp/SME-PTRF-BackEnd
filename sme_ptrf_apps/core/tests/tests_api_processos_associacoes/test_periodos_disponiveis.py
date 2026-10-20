import pytest
from model_bakery import baker
from rest_framework import status
from waffle.testutils import override_flag

from sme_ptrf_apps.core.models import Recurso

pytestmark = pytest.mark.django_db


def get_uuids(result):
    return [periodo['uuid'] for periodo in result]


def test_periodos_disponiveis(
    jwt_authenticated_client_a,
    associacao,
    processo_associacao_123456_2019,
    periodo_anterior,
    periodo_2019_1,
    periodo_2019_2,
    periodo_factory,
):
    periodo_2019_3 = periodo_factory(referencia='2019.3')

    url = f'/api/processos-associacao/periodos-disponiveis/?associacao_uuid={associacao.uuid}&ano=2019'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = get_uuids(result)

    assert str(periodo_2019_3.uuid) in uuids
    assert str(periodo_2019_1.uuid) not in uuids
    assert str(periodo_2019_2.uuid) not in uuids
    assert str(periodo_anterior.uuid) not in uuids


def test_periodos_disponiveis_edicao_do_proprio_processo(
    jwt_authenticated_client_a,
    associacao,
    processo_associacao_123456_2019,
    periodo_2019_1,
    periodo_2019_2,
):
    url = (
        f'/api/processos-associacao/periodos-disponiveis/'
        f'?associacao_uuid={associacao.uuid}&ano=2019&processo_uuid={processo_associacao_123456_2019.uuid}'
    )
    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = get_uuids(result)

    assert str(periodo_2019_1.uuid) in uuids
    assert str(periodo_2019_2.uuid) in uuids


def test_periodos_disponiveis_sem_parametros_obrigatorios(jwt_authenticated_client_a, associacao):
    response = jwt_authenticated_client_a.get(
        '/api/processos-associacao/periodos-disponiveis/', content_type='application/json')

    assert response.status_code == 400
    assert 'erro' in response.json()


def test_periodos_disponiveis_flag_ativa_com_recurso_uuid(
    jwt_authenticated_client_a,
    associacao,
    periodo_factory,
):
    outro_recurso = baker.make(
        'Recurso',
        nome_exibicao='Outro Recurso',
        cor=Recurso.CorChoices.VERDE,
    )
    periodo_outro_recurso = periodo_factory(referencia='2021.1', recurso=outro_recurso)

    with override_flag('premio-excelencia-processo-sei', active=True):
        url = (
            f'/api/processos-associacao/periodos-disponiveis/'
            f'?associacao_uuid={associacao.uuid}&ano=2021&recurso_uuid={outro_recurso.uuid}'
        )
        response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert str(periodo_outro_recurso.uuid) in get_uuids(result)


def test_periodos_disponiveis_flag_ativa_sem_recurso_uuid(
    jwt_authenticated_client_a,
    associacao,
    periodo_factory,
):
    periodo_legado = periodo_factory(referencia='2022.1')

    with override_flag('premio-excelencia-processo-sei', active=True):
        url = f'/api/processos-associacao/periodos-disponiveis/?associacao_uuid={associacao.uuid}&ano=2022'
        response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert str(periodo_legado.uuid) in get_uuids(result)
