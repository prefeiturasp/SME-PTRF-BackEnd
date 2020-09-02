import json

import pytest
from rest_framework import status

from ...api.serializers import PrestacaoContaLookUpSerializer
from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


def test_api_reabre_prestacao_conta(client, prestacao_conta):
    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/reabrir/'

    response = client.patch(url, content_type='application/json')

    result = json.loads(response.content)

    prestacao_atualizada = PrestacaoConta.by_uuid(uuid=prestacao_conta.uuid)

    result_esperado = PrestacaoContaLookUpSerializer(
        prestacao_atualizada,
        many=False).data

    # Converto os campos UUIDs em strings para que a comparação funcione
    result_esperado['periodo_uuid'] = f'{result_esperado["periodo_uuid"]}'

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a prestação de contas esperada."
