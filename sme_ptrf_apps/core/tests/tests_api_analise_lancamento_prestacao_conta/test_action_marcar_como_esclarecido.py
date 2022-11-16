import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_marcar_como_esclarecido(
    solicitacao_acerto_lancamento_devolucao,
    jwt_authenticated_client_a
):

    payload = {
        'esclarecimento': "Este é o esclarecimento",
        'uuid_solicitacao_acerto': f"{solicitacao_acerto_lancamento_devolucao.uuid}"
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-lancamento-prestacao-conta/marcar-como-esclarecido/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
