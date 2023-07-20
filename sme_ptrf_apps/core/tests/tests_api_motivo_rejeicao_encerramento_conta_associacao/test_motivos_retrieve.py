import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_motivo(
    jwt_authenticated_client_a,
    motivo_rejeicao
):
    response = jwt_authenticated_client_a.get(
        f'/api/motivos-rejeicao-encerramento-conta/{motivo_rejeicao.uuid}/', content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['uuid']
