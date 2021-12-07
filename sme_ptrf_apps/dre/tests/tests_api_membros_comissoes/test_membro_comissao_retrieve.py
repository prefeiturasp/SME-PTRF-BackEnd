import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_membro_comissao(
    jwt_authenticated_client_dre,
    membro_alex_comissao_a_dre_x,
    membro_beto_comissao_a_b_dre_x,
    dre_x,
    comissao_a
):
    response = jwt_authenticated_client_dre.get(
        f'/api/membros-comissoes/{membro_alex_comissao_a_dre_x.uuid}/', content_type='application/json')
    result = json.loads(response.content)
    esperado = {
        'uuid': f'{membro_alex_comissao_a_dre_x.uuid}',
        'rf': '123457',
        'nome': 'Alex',
        'email': 'alex@teste.com',
        'dre': {
            'codigo_eol': '812345',
            'dre': None,
            'nome': 'X',
            'sigla': 'X',
            'tipo_unidade': 'DRE',
            'uuid': f'{dre_x.uuid}'
        },
        'qtd_comissoes': 1,
        'comissoes': [
            {
                'nome': 'A',
                'id': comissao_a.id,
                'uuid': f'{comissao_a.uuid}'
            }
        ],
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
