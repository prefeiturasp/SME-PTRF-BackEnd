import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

def test_api_retrieve_associacao(client, associacao):
    response = client.get(f'/api/associacoes/', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = [
        {
            'uuid': f'{associacao.uuid}',
            'nome': associacao.nome,
            'unidade': {
                'uuid': f'{associacao.unidade.uuid}',
                'codigo_eol': associacao.unidade.codigo_eol,
                'nome_com_tipo': associacao.unidade.nome_com_tipo
            },
            'status_regularidade': associacao.status_regularidade,
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado
