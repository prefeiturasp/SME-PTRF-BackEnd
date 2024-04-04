import json

import pytest
from rest_framework import status
from waffle.testutils import override_flag

from sme_ptrf_apps.core.models import ProcessoAssociacao

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_processo_associacao(associacao):
    payload = {
        'associacao': str(associacao.uuid),
        'numero_processo': "271170",
        'ano': '2020'
    }
    return payload

@pytest.fixture
def payload_processo_associacao_com_periodo(associacao, periodo_2020_1):
    payload = {
        'associacao': str(associacao.uuid),
        'numero_processo': "271170",
        'ano': '2020',
        'periodos': [str(periodo_2020_1.uuid)]
    }
    return payload


def test_update_processo_associacao(jwt_authenticated_client_a, associacao, processo_associacao_123456_2019,
                                    payload_processo_associacao):
    numero_processo_novo = "190889"
    payload_processo_associacao['numero_processo'] = numero_processo_novo
    response = jwt_authenticated_client_a.put(
        f'/api/processos-associacao/{processo_associacao_123456_2019.uuid}/',
        data=json.dumps(payload_processo_associacao),
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    assert ProcessoAssociacao.objects.filter(uuid=result['uuid']).exists()

    processo = ProcessoAssociacao.objects.filter(uuid=result['uuid']).get()

    assert processo.numero_processo == numero_processo_novo


def test_update_processo_associacao_sem_periodos_com_flag_ligada(jwt_authenticated_client_a, associacao, processo_associacao_123456_2019,
                                    payload_processo_associacao):
    with override_flag('periodos-processo-sei', active=True):
        numero_processo_novo = "190889"
        payload_processo_associacao['numero_processo'] = numero_processo_novo
        response = jwt_authenticated_client_a.put(
            f'/api/processos-associacao/{processo_associacao_123456_2019.uuid}/',
            data=json.dumps(payload_processo_associacao),
            content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        result = json.loads(response.content)
        assert result == {'periodos': ["É necessário informar ao menos um período quando a feature 'periodos-processo-sei' está ativa."]}

