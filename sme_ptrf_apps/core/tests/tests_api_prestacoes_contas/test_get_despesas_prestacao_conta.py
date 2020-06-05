import json

import pytest
from rest_framework import status

from ....despesas.api.serializers.rateio_despesa_serializer import RateioDespesaListaSerializer

pytestmark = pytest.mark.django_db


def test_api_get_despesas_conferidas_prestacao_conta(client,
                                                    acao_associacao_role_cultural,
                                                    prestacao_conta_iniciada,
                                                    despesa_2019_2,
                                                    rateio_despesa_2019_role_conferido,
                                                    despesa_2020_1,
                                                    rateio_despesa_2020_role_conferido,
                                                    rateio_despesa_2020_role_nao_conferido,
                                                    rateio_despesa_2020_ptrf_conferido,
                                                    rateio_despesa_2020_role_cheque_conferido
                                                    ):
    prestacao_uuid = prestacao_conta_iniciada.uuid
    acao_uuid = acao_associacao_role_cultural.uuid

    url = f'/api/prestacoes-contas/{prestacao_uuid}/despesas/?acao_associacao_uuid={acao_uuid}&conferido=True'

    response = client.get(url, content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = []
    result_esperado = RateioDespesaListaSerializer(rateio_despesa_2020_role_conferido, many=False).data
    # Converto os campos não string em strings para que a comparação funcione
    result_esperado['data_documento'] = f'{result_esperado["data_documento"]}'
    result_esperado['data_transacao'] = f'{result_esperado["data_transacao"]}'
    result_esperado['despesa'] = f'{result_esperado["despesa"]}'

    resultado_esperado.append(result_esperado)

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado, "Não retornou a lista de despesas esperada."
