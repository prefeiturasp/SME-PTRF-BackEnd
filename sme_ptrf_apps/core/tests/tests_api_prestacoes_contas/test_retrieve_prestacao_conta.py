import json

import pytest
from rest_framework import status

from ...api.serializers import PrestacaoContaLookUpSerializer
from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


def test_api_retrieve_prestacao_conta_por_periodo_e_associacao(client, prestacao_conta, prestacao_conta_anterior):
    associacao_uuid = prestacao_conta.associacao.uuid
    periodo_uuid = prestacao_conta.periodo.uuid

    url = f'/api/prestacoes-contas/por-associacao-e-periodo/?associacao_uuid={associacao_uuid}&periodo_uuid={periodo_uuid}'

    response = client.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = PrestacaoContaLookUpSerializer(PrestacaoConta.objects.get(uuid=prestacao_conta.uuid), many=False).data

    # Converto os campos UUIDs em strings para que a comparação funcione
    result_esperado['periodo_uuid'] = f'{result_esperado["periodo_uuid"]}'

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado
