import json

import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import ComentarioAnalisePrestacao

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_comentario(prestacao_conta_2020_1_conciliada):
    payload = {
        'prestacao_conta': f'{prestacao_conta_2020_1_conciliada.uuid}',
        'ordem': 1,
        'comentario': 'Teste'
    }
    return payload


def test_create_comentario_analise_prestacao(jwt_authenticated_client, payload_comentario):
    response = jwt_authenticated_client.post(
        '/api/comentarios-de-analises/', data=json.dumps(payload_comentario), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert ComentarioAnalisePrestacao.objects.filter(uuid=result['uuid']).exists()
