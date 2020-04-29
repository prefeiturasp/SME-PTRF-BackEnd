import json

import pytest
from rest_framework import status

from ...models import Associacao
from ...api.serializers import AssociacaoSerializer

pytestmark = pytest.mark.django_db


def test_api_retrieve_associacao(client, associacao):
    response = client.get(f'/api/associacoes/{associacao.uuid}/', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = AssociacaoSerializer(Associacao.objects.get(uuid=associacao.uuid), many=False).data

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado
