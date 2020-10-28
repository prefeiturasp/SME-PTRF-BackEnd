import pytest
from rest_framework import status

from ...models import Despesa

pytestmark = pytest.mark.django_db


def test_api_delete_despesas(
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
):
    assert Despesa.objects.filter(uuid=despesa.uuid).exists()

    response = jwt_authenticated_client_d.delete(f'/api/despesas/{despesa.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Despesa.objects.filter(uuid=despesa.uuid).exists()
