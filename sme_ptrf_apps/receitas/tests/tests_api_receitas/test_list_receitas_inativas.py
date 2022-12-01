import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_list_receitas_inativas(
    jwt_authenticated_client_p,
    associacao,
    receita_inativa,
    receita_ativa
):
    response = jwt_authenticated_client_p.get(
        f'/api/receitas/?associacao__uuid={associacao.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK

    # Retorna apenas a receita ativa
    assert len(result) == 1
    assert not [d for d in result if d['status'] == 'INATIVO']
