import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_list_faqs_todos(client, faq, faq_02):
    response = client.get(f'/api/faqs/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "uuid": f'{faq.uuid}',
            "pergunta": f'{faq.pergunta}',
            "resposta": f'{faq.resposta}',
        },
        {
            "uuid": f'{faq_02.uuid}',
            "pergunta": f'{faq_02.pergunta}',
            "resposta": f'{faq_02.resposta}',
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado



def test_api_list_faqs_por_categoria(client, faq, faq_categoria):
    response = client.get(f'/api/faqs/?categoria__uuid={faq_categoria.uuid}', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "uuid": f'{faq.uuid}',
            "pergunta": f'{faq.pergunta}',
            "resposta": f'{faq.resposta}',
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
