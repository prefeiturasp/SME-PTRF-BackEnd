import json

import pytest
from rest_framework import status
from waffle.testutils import override_flag

from ...models import Despesa

pytestmark = pytest.mark.django_db


@override_flag('ajustes-despesas-anteriores', active=True)
def test_api_post_despesa_anterior_ao_uso_do_sistema(
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
    payload_despesa_anterior_ao_uso_do_sistema
):
    response = jwt_authenticated_client_d.post('/api/despesas/', data=json.dumps(payload_despesa_anterior_ao_uso_do_sistema), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Despesa.objects.filter(uuid=result["uuid"]).exists()

    despesa = Despesa.objects.get(uuid=result["uuid"])

    assert despesa.despesa_anterior_ao_uso_do_sistema

