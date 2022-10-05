import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_marcar_como_esclarecido(
    analise_lancamento_despesa_prestacao_conta_2020_1,
    jwt_authenticated_client_a
):
    uuid_analise = f"{analise_lancamento_despesa_prestacao_conta_2020_1.uuid}"

    payload = {
        'esclarecimento': "Este é o esclarecimento"
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-lancamento-prestacao-conta/{uuid_analise}/marcar-como-esclarecido/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
