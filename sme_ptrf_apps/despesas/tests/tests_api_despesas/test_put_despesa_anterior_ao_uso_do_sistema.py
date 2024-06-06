import json

import pytest
from rest_framework import status
from waffle.testutils import override_flag

from ...models import Despesa

pytestmark = pytest.mark.django_db


@override_flag('ajustes-despesas-anteriores', active=True)
def test_api_put_despesa_anterior_ao_uso_do_sistema(
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    despesa,
    rateio_despesa_capital,
    payload_despesa_anterior_ao_uso_do_sistema,
):

    response = jwt_authenticated_client_d.put(f'/api/despesas/{despesa.uuid}/', data=json.dumps(payload_despesa_anterior_ao_uso_do_sistema),
                          content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    despesa = Despesa.objects.get(uuid=result["uuid"])

    assert despesa.despesa_anterior_ao_uso_do_sistema
