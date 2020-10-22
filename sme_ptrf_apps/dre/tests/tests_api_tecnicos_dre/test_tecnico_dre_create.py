import json

import pytest
from rest_framework import status

from sme_ptrf_apps.dre.models import TecnicoDre

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_tecnico_dre(dre_butantan):
    payload = {
        'dre': f'{dre_butantan.uuid}',
        'rf': '1234567',
        'nome': 'Pedro Antunes',
        'email': 'tecnico.sobrenome@sme.prefeitura.sp.gov.br',
    }
    return payload


def test_create_tecnico_dre(jwt_authenticated_client, dre, payload_tecnico_dre):
    response = jwt_authenticated_client.post(
        '/api/tecnicos-dre/', data=json.dumps(payload_tecnico_dre), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert TecnicoDre.objects.filter(uuid=result['uuid']).exists()


@pytest.fixture
def payload_tecnico_dre_rf_ja_existente(dre_butantan, tecnico_maria_dre_butantan):
    payload = {
        'dre': f'{dre_butantan.uuid}',
        'rf': tecnico_maria_dre_butantan.rf,
        'nome': 'Pedro Antunes',
        'email': tecnico_maria_dre_butantan.email
    }
    return payload


def test_create_tecnico_dre_repetido(jwt_authenticated_client, dre, tecnico_maria_dre_butantan,
                                     payload_tecnico_dre_rf_ja_existente):
    response = jwt_authenticated_client.post(
        '/api/tecnicos-dre/', data=json.dumps(payload_tecnico_dre_rf_ja_existente), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    assert result == {'rf': ['Técnico de DRE with this RF already exists.']}
