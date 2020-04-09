import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_receitas_por_tipo_receita(client,
                                           tipo_receita_estorno,
                                           tipo_receita_repasse,
                                           receita_xxx_estorno,
                                           receita_yyy_repasse,
                                           acao,
                                           acao_associacao,
                                           associacao,
                                           tipo_conta,
                                           conta_associacao):
    response = client.get(f'/api/receitas/?tipo_receita={tipo_receita_estorno.id}',
                          content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1
