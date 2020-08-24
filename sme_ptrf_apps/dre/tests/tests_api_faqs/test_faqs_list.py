import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_list_faqs_todos(client, faq_01, faq_02):
    response = client.get(f'/api/faqs/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "uuid": f'{faq_01.uuid}',
            "pergunta": f'{faq_01.pergunta}',
            "resposta": f'{faq_01.resposta}',
        },
        {
            "uuid": f'{faq_02.uuid}',
            "pergunta": f'{faq_02.pergunta}',
            "resposta": f'{faq_02.resposta}',
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado



def test_api_list_faqs_por_categoria(client, faq_01, cat_01):
    response = client.get(f'/api/faqs/?categoria__uuid={cat_01.uuid}', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "uuid": f'{faq_01.uuid}',
            "pergunta": f'{faq_01.pergunta}',
            "resposta": f'{faq_01.resposta}',
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
