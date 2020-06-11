import json

import pytest
from rest_framework import status

from ...api.serializers.rateio_despesa_serializer import RateioDespesaListaSerializer
from ...models import RateioDespesa

pytestmark = pytest.mark.django_db


def test_api_rateio_conciliar_despesa_com_prestacao_de_conta(client, rateio_despesa_nao_conferido,
                                                             prestacao_conta_iniciada):
    rateio_uuid = rateio_despesa_nao_conferido.uuid

    url = f'/api/rateios-despesas/{rateio_uuid}/conciliar/?prestacao_conta_uuid={prestacao_conta_iniciada.uuid}'

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
    assert rateio_conciliado.prestacao_conta == prestacao_conta_iniciada, \
        "Rateio deveria ter sido vinculada à prestacao de contas."


def test_api_conciliar_despesa_sem_prestacao_conta(client, rateio_despesa_nao_conferido):
    rateio_uuid = rateio_despesa_nao_conferido.uuid

    url = f'/api/rateios-despesas/{rateio_uuid}/conciliar/'

    response = client.patch(url, content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        'erro': 'parametros_requerido',
        'mensagem': 'É necessário enviar o uuid da prestação de contas onde esta sendo feita a conciliação.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado
