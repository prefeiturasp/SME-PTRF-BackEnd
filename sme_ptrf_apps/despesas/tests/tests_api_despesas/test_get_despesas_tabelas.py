import json

import pytest
from rest_framework import status

from ...tipos_aplicacao_recurso import APLICACAO_CUSTEIO, APLICACAO_CAPITAL, APLICACAO_NOMES

pytestmark = pytest.mark.django_db


def test_api_get_despesas_tabelas(associacao, jwt_authenticated_client, tipo_aplicacao_recurso, tipo_custeio, tipo_documento, tipo_transacao, acao,
                                  acao_associacao, tipo_conta, conta_associacao):
    response = jwt_authenticated_client.get('/api/despesas/tabelas/', content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'tipos_aplicacao_recurso': [
            {
                'id': APLICACAO_CAPITAL,
                'nome': APLICACAO_NOMES[APLICACAO_CAPITAL]
            },
            {
                'id': APLICACAO_CUSTEIO,
                'nome': APLICACAO_NOMES[APLICACAO_CUSTEIO]
            }
        ],

        'tipos_custeio': [
            {
                'id': tipo_custeio.id,
                'nome': tipo_custeio.nome
            },
        ],

        'tipos_documento': [
            {
                'id': tipo_documento.id,
                'nome': tipo_documento.nome
            },
        ],

        'tipos_transacao': [
            {
                'id': tipo_transacao.id,
                'nome': tipo_transacao.nome
            },
        ],

        'acoes_associacao': [
            {
                'uuid': f'{acao_associacao.uuid}',
                'id': acao_associacao.id,
                'nome': acao_associacao.acao.nome
            },
        ],

        'contas_associacao': [
            {
                'uuid': f'{conta_associacao.uuid}',
                'nome': conta_associacao.tipo_conta.nome
            },
        ]

    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
