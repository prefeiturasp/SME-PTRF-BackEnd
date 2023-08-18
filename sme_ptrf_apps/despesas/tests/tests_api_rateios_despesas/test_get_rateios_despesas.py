import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_rateios_despesas(jwt_authenticated_client_d, associacao, despesa, rateio_despesa_capital, conta_associacao):
    response = jwt_authenticated_client_d.get(f'/api/rateios-despesas/?associacao_uuid={associacao.uuid}', content_type='application/json')
    result = json.loads(response.content)

    uuids_esperado = [f'{rateio_despesa_capital.uuid}']

    result_uuids = []
    for item in result:
        result_uuids.append(item['uuid'])

    assert response.status_code == status.HTTP_200_OK
    assert result_uuids == uuids_esperado
