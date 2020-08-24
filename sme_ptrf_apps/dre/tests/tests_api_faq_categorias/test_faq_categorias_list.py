import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_list_faq_categorias(client, cat_01, cat_02):
    response = client.get(f'/api/faq-categorias/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "uuid": f'{cat_01.uuid}',
            "nome": cat_01.nome,
        },
        {
            "uuid": f'{cat_02.uuid}',
            "nome": cat_02.nome,
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
