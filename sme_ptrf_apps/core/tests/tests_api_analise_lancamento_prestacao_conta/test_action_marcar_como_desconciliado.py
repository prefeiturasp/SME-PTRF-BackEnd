import pytest
from rest_framework import status
import json

pytestmark = pytest.mark.django_db


def test_marcar_lancamento_como_desconciliado(
    analise_lancamento_despesa_prestacao_conta_2020_1,
    jwt_authenticated_client_a
):

    payload = {
        "uuid_analise_lancamento": f"{analise_lancamento_despesa_prestacao_conta_2020_1.uuid}",
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-lancamento-prestacao-conta/marcar-como-desconciliado/',
        data=json.dumps(payload),
        content_type='application/json'
    )


    assert response.status_code == status.HTTP_200_OK

