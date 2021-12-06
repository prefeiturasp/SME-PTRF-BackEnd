import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_list_comissoes(jwt_authenticated_client_dre, comissao_exame_contas):
    response = jwt_authenticated_client_dre.get(f'/api/comissoes/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "nome": comissao_exame_contas.nome,
            "uuid": f'{comissao_exame_contas.uuid}',
            "id": comissao_exame_contas.id,
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
