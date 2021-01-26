import json

import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_acoes_list_associacoes_nao_vinculadas(jwt_authenticated_client_a,
                                                   acao_x,
                                                   acao_y,
                                                   associacao_charli_bravo_000086,
                                                   associacao_eco_delta_000087,
                                                   acao_associacao_charli_bravo_000086_y,
                                                   acao_associacao_charli_bravo_000086_x,
                                                   acao_associacao_eco_delta_000087_x
                                                   ):
    response = jwt_authenticated_client_a.get(f'/api/acoes/{acao_y.uuid}/associacoes-nao-vinculadas/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'uuid': f'{associacao_eco_delta_000087.uuid}',
            'nome': associacao_eco_delta_000087.nome,
            'unidade': {
                'uuid': f'{associacao_eco_delta_000087.unidade.uuid}',
                'codigo_eol': associacao_eco_delta_000087.unidade.codigo_eol,
                'nome_com_tipo': associacao_eco_delta_000087.unidade.nome_com_tipo
            },
            'status_regularidade': associacao_eco_delta_000087.status_regularidade,
            'motivo_nao_regularidade': '',
            'cnpj': associacao_eco_delta_000087.cnpj
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
