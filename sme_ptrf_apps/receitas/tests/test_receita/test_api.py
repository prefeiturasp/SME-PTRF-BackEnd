import json

import pytest
from rest_framework import status
from rest_framework.response import Response

from sme_ptrf_apps.receitas.models import Receita

pytestmark = pytest.mark.django_db


def test_create_receita(
    client,
    tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_receita
):
    response = client.post('/api/receitas/', data=json.dumps(payload_receita), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Receita.objects.filter(uuid=result["uuid"]).exists()

    receita = Receita.objects.get(uuid=result["uuid"])

    assert receita.associacao.uuid == associacao.uuid


def test_get_tabelas(
    client,
    tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao):

    response = client.get('/api/receitas/tabelas/', content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'tipos_receita': [
            {
                'id': tipo_receita.id,
                'nome': tipo_receita.nome
            },
        ],

        'acoes_associacao': [
            {
                'uuid': f'{acao_associacao.uuid}',
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


def test_get_receitas(
    client,
    tipo_receita,
    receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao):
    response = client.get('/api/receitas/', content_type='application/json')
    result = json.loads(response.content)

    results = [
        {
            'uuid': str(receita.uuid),
            'data': '2020-03-26',
            'valor': '100.00',
            'tipo_receita': {
                'id': tipo_receita.id,
                'nome': tipo_receita.nome
            },
            "acao_associacao": {
                "uuid": str(acao_associacao.uuid),
                "nome": acao_associacao.acao.nome
            },
            'conta_associacao': {
                "uuid": str(conta_associacao.uuid),
                "nome": conta_associacao.tipo_conta.nome
            } 		
        },
    ]

    esperado = {
        'count': 1,
        'next': None,
        'previous': None,
        'results': results
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_update_receita(
    client,
    tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    receita,
    payload_receita
):
    response = client.put(f'/api/receitas/{receita.uuid}/', data=json.dumps(payload_receita),
                          content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    receita = Receita.objects.get(uuid=result["uuid"])

    assert receita.associacao.uuid == associacao.uuid
