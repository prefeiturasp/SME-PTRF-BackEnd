import json

import pytest
from rest_framework import status

from sme_ptrf_apps.dre.models import TecnicoDre

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_tecnico_altera_nome_para_pedro(dre_butantan):
    payload = {
        'nome': 'Pedro'
    }
    return payload


def test_update_tecnico_dre(jwt_authenticated_client, dre_butantan, tecnico_maria_dre_butantan,
                            payload_tecnico_altera_nome_para_pedro):

    response = jwt_authenticated_client.put(
        f'/api/tecnicos-dre/{tecnico_maria_dre_butantan.uuid}/',
        data=json.dumps(payload_tecnico_altera_nome_para_pedro),
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    tecnico = TecnicoDre.objects.get(uuid=result['uuid'])

    assert tecnico.nome == 'Pedro'
