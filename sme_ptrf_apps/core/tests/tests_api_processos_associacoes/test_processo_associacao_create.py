import json
import pytest

from model_bakery import baker
from rest_framework import status
from waffle.testutils import override_flag

from sme_ptrf_apps.core.models import ProcessoAssociacao

pytestmark = pytest.mark.django_db

@pytest.fixture
def payload_processo_associacao_sem_periodos(associacao):
    payload = {
        'associacao': str(associacao.uuid),
        'numero_processo': "271170",
        'ano': '2020'
    }
    return payload


@pytest.fixture
def payload_processo_associacao_com_periodos(associacao, periodo):
    payload = {
        'associacao': str(associacao.uuid),
        'numero_processo': "271170",
        'ano': '2019',
        'periodos': [str(periodo.uuid)]
    }
    return payload


@pytest.fixture
def payload_processo_associacao_com_periodos_de_outro_ano(associacao, periodo, periodo_2020_1):
    payload = {
        'associacao': str(associacao.uuid),
        'numero_processo': "271170",
        'ano': '2019',
        'periodos': [str(periodo.uuid), str(periodo_2020_1.uuid)]
    }
    return payload

@pytest.fixture
def processo_associacao_usando_o_mesmo_periodo(associacao, periodo):
    return baker.make(
        'ProcessoAssociacao',
        associacao=associacao,
        numero_processo='123456',
        ano='2019',
        periodos=[periodo,],
    )


def test_create_processo_associacao_servidor_sem_periodos_com_flag_desligada(jwt_authenticated_client_a, associacao,
                                                                             payload_processo_associacao_sem_periodos):
    response = jwt_authenticated_client_a.post(
        '/api/processos-associacao/', data=json.dumps(payload_processo_associacao_sem_periodos), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert ProcessoAssociacao.objects.filter(uuid=result['uuid']).exists()


def test_create_processo_associacao_servidor_sem_periodos_com_flag_ligada(jwt_authenticated_client_a, associacao,
                                                                          payload_processo_associacao_sem_periodos):
    with override_flag('periodos-processo-sei', active=True):
        response = jwt_authenticated_client_a.post(
            '/api/processos-associacao/', data=json.dumps(payload_processo_associacao_sem_periodos), content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_processo_associacao_servidor_com_periodos_com_flag_ligada(jwt_authenticated_client_a, associacao,
                                                                          payload_processo_associacao_com_periodos):
    with override_flag('periodos-processo-sei', active=True):
        response = jwt_authenticated_client_a.post(
            '/api/processos-associacao/', data=json.dumps(payload_processo_associacao_com_periodos),
            content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED

        result = json.loads(response.content)

        assert ProcessoAssociacao.objects.filter(uuid=result['uuid']).exists()

        # Assert se o processo foi criado com os periodos vinculados
        processo = ProcessoAssociacao.objects.get(uuid=result['uuid'])
        assert processo.periodos.count() == 1
        assert str(processo.periodos.first().uuid) == payload_processo_associacao_com_periodos['periodos'][0]


def test_create_processo_associacao_servidor_com_periodos_com_flag_desligada(jwt_authenticated_client_a, associacao,
                                                                          payload_processo_associacao_com_periodos):
    response = jwt_authenticated_client_a.post(
        '/api/processos-associacao/', data=json.dumps(payload_processo_associacao_com_periodos),
        content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_processo_associacao_servidor_com_periodos_de_outro_ano(jwt_authenticated_client_a, associacao,
                                                                          payload_processo_associacao_com_periodos_de_outro_ano):
    with override_flag('periodos-processo-sei', active=True):
        response = jwt_authenticated_client_a.post(
            '/api/processos-associacao/', data=json.dumps(payload_processo_associacao_com_periodos_de_outro_ano), content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        result = json.loads(response.content)
        assert result == {
            'periodos': ["Todos os períodos devem estar no mesmo ano do campo 'ano' (2019)."]}


def test_create_processo_associacao_servidor_com_periodo_ja_usado(
    jwt_authenticated_client_a,
    associacao,
    payload_processo_associacao_com_periodos,
    processo_associacao_usando_o_mesmo_periodo
):
    with override_flag('periodos-processo-sei', active=True):
        response = jwt_authenticated_client_a.post(
            '/api/processos-associacao/', data=json.dumps(payload_processo_associacao_com_periodos), content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        result = json.loads(response.content)
        assert result == {'periodos': ['O período 2019.2 já está associado a outro ProcessoAssociacao '
                                       'para a associação Escola Teste.']}
