import json
import pytest

from rest_framework import status


from sme_ptrf_apps.core.models import Acao

pytestmark = pytest.mark.django_db


def test_create_acao(
    jwt_authenticated_client_a,
):
    payload_acao_nova = {
        'nome': 'Nova',
        'e_recursos_proprios': False,
    }
    response = jwt_authenticated_client_a.post(
        '/api/acoes/', data=json.dumps(payload_acao_nova), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Acao.objects.filter(uuid=result['uuid']).exists()


def test_create_acao_nome_igual(
    jwt_authenticated_client_a,
    acao_xpto
):
    payload_acao_nova = {
        'nome': 'Xpto',
        'e_recursos_proprios': False,
    }
    response = jwt_authenticated_client_a.post(
        '/api/acoes/', data=json.dumps(payload_acao_nova), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)
    assert result == {'non_field_errors': ['The fields nome must make a unique set.']}
