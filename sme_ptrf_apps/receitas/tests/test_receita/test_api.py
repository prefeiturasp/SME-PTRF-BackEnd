import json

import pytest
from rest_framework import status

from sme_ptrf_apps.receitas.models import Receita, Repasse

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

def test_create_receita_repasse(
    client,
    tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    repasse,
    payload_receita_repasse
):
    assert Repasse.objects.get(uuid=repasse.uuid).status == 'PENDENTE'

    response = client.post('/api/receitas/', data=json.dumps(payload_receita_repasse), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Receita.objects.filter(uuid=result["uuid"]).exists()

    receita = Receita.objects.get(uuid=result["uuid"])

    assert receita.associacao.uuid == associacao.uuid

    assert Repasse.objects.get(uuid=repasse.uuid).status == 'REALIZADO'


def test_create_receita_repasse_periodo_invalido(
    client,
    tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    repasse,
    payload_receita_repasse
):

    payload_receita_repasse['data'] = '2020-01-11'
    response = client.post('/api/receitas/', data=json.dumps(payload_receita_repasse), content_type='application/json')
    result = json.loads(response.content)

    assert result == ['Repasse não encontrado.']
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_receita_repasse_valor_diferente(
    client,
    tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    repasse,
    payload_receita_repasse
):

    payload_receita_repasse['valor'] = 2000.67
    response = client.post('/api/receitas/', data=json.dumps(payload_receita_repasse), content_type='application/json')
    result = json.loads(response.content)

    assert result == ['Valor do payload não é igual ao valor total do repasse.']
    assert response.status_code == status.HTTP_400_BAD_REQUEST


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
                'nome': tipo_receita.nome,
                'e_repasse': tipo_receita.e_repasse
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
            'descricao': "Uma receita",
            'tipo_receita': {
                'id': tipo_receita.id,
                'nome': tipo_receita.nome,
                'e_repasse': tipo_receita.e_repasse
            },
            "acao_associacao": {
                "uuid": str(acao_associacao.uuid),
                "id": acao_associacao.id,
                "nome": acao_associacao.acao.nome
            },
            'conta_associacao': {
                "uuid": str(conta_associacao.uuid),
                "nome": conta_associacao.tipo_conta.nome
            }
        },
    ]

    esperado = results

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


def test_deleta_receita(
    client,
    tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    receita,
    payload_receita):

    assert Receita.objects.filter(uuid=receita.uuid).exists()

    response = client.delete(f'/api/receitas/{receita.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Receita.objects.filter(uuid=receita.uuid).exists()


def test_deleta_receita_repasse(
    client,
    tipo_receita_repasse,
    acao,
    acao_associacao_role_cultural,
    associacao,
    tipo_conta_cartao,
    conta_associacao_cartao,
    receita_yyy_repasse,
    repasse_realizado
    ):

    assert Repasse.objects.get(uuid=repasse_realizado.uuid).status == 'REALIZADO'

    assert Receita.objects.filter(uuid=receita_yyy_repasse.uuid).exists()

    response = client.delete(f'/api/receitas/{receita_yyy_repasse.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Receita.objects.filter(uuid=receita_yyy_repasse.uuid).exists()

    assert Repasse.objects.get(uuid=repasse_realizado.uuid).status == 'PENDENTE'


def test_retrive_receitas(
    client,
    tipo_receita,
    receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao):

    response = client.get(f'/api/receitas/{receita.uuid}/', content_type='application/json')
    result = json.loads(response.content)

    esperado = {
            'uuid': str(receita.uuid),
            'data': '2020-03-26',
            'valor': '100.00',
            'descricao': "Uma receita",
            'tipo_receita': {
                'id': tipo_receita.id,
                'nome': tipo_receita.nome,
                'e_repasse': tipo_receita.e_repasse
            },
            "acao_associacao": {
                "uuid": str(acao_associacao.uuid),
                "id": acao_associacao.id,
                "nome": acao_associacao.acao.nome
            },
            'conta_associacao': {
                "uuid": str(conta_associacao.uuid),
                "nome": conta_associacao.tipo_conta.nome
            }
        }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
