import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

def test_api_list_motivos(jwt_authenticated_client, motivo_rejeicao):
    response = jwt_authenticated_client.get('/api/motivos-rejeicao-encerramento-conta/', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['results']
    assert result['count'] == 1

def test_api_list_motivos_filter_nome(jwt_authenticated_client, motivo_rejeicao, motivo_rejeicao_2):
    response = jwt_authenticated_client.get('/api/motivos-rejeicao-encerramento-conta/?nome=pix', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['results']
    assert result['count'] == 1
