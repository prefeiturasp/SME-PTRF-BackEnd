import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

def test_create_motivo(
    jwt_authenticated_client_a,
    payload_motivo_rejeicao_valido
):
    response = jwt_authenticated_client_a.post(
        '/api/motivos-rejeicao-encerramento-conta/', data=json.dumps(payload_motivo_rejeicao_valido), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

def test_validacao_nome_create_motivo(
    jwt_authenticated_client_a,
    payload_motivo_rejeicao_invalido,
    motivo_rejeicao
):
    response = jwt_authenticated_client_a.post(
        '/api/motivos-rejeicao-encerramento-conta/', data=json.dumps(payload_motivo_rejeicao_invalido), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

