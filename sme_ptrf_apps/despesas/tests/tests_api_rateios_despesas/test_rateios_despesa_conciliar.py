import json

import pytest
from rest_framework import status

from ...api.serializers.rateio_despesa_serializer import RateioDespesaListaSerializer
from ...models import RateioDespesa

pytestmark = pytest.mark.django_db


def test_api_rateio_conciliar_despesa(client, rateio_despesa_nao_conferido):
    rateio_uuid = rateio_despesa_nao_conferido.uuid

    url = f'/api/rateios-despesas/{rateio_uuid}/conciliar/'

    response = client.patch(url, content_type='application/json')

    result = json.loads(response.content)

    rateio_conciliado = RateioDespesa.by_uuid(rateio_uuid)
    result_esperado = RateioDespesaListaSerializer(rateio_conciliado, many=False).data

    # Converte campos não string em strings para que a comparação funcione
    result_esperado['despesa'] = f'{result_esperado["despesa"]}'
    result_esperado['data_documento'] = f'{result_esperado["data_documento"]}'
    result_esperado['data_transacao'] = f'{result_esperado["data_transacao"]}'

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado

    assert rateio_conciliado.conferido, "Rateio deveria ter sido marcado como conferido."
