import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_list_faq_categorias(client, faq_categoria, faq_categoria_02):
    response = client.get(f'/api/faq-categorias/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "uuid": f'{faq_categoria.uuid}',
            "nome": faq_categoria.nome,
        },
        {
            "uuid": f'{faq_categoria_02.uuid}',
            "nome": faq_categoria_02.nome,
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
