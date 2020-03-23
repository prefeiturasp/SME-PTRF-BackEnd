import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_despesas_tabelas(client, tipo_aplicacao_recurso, tipo_custeio, tipo_documento, tipo_transacao, acao,
                                  acao_associacao, associacao, tipo_conta, conta_associacao):
    response = client.get('/api/despesas/tabelas/', content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'tipos_aplicacao_recurso': [
            {
                'id': tipo_aplicacao_recurso.id,
                'nome': tipo_aplicacao_recurso.nome
            },
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
                'id': acao_associacao.id,
                'nome': acao_associacao.acao.nome
            },
        ],

        'contas_associacao': [
            {
                'id': conta_associacao.id,
                'nome': conta_associacao.tipo_conta.nome
            },
        ]

    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
