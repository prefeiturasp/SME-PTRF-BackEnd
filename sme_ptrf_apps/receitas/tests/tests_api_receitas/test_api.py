import json

import pytest
from freezegun import freeze_time
from rest_framework import status

from sme_ptrf_apps.receitas.models import Receita, Repasse

pytestmark = pytest.mark.django_db


def test_create_receita(
    client,
    tipo_receita,
    detalhe_tipo_receita,
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
    assert receita.detalhe_tipo_receita == detalhe_tipo_receita


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
    with freeze_time('2019-11-29'):
        assert Repasse.objects.get(uuid=repasse.uuid).status == 'PENDENTE'

        response = client.post('/api/receitas/', data=json.dumps(payload_receita_repasse),
                               content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED

        result = json.loads(response.content)

        assert Receita.objects.filter(uuid=result["uuid"]).exists()

        receita = Receita.objects.get(uuid=result["uuid"])

        assert receita.associacao.uuid == associacao.uuid

        assert Repasse.objects.get(uuid=repasse.uuid).status == 'PENDENTE'


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
    payload_receita_repasse['data'] = '2020-09-02'
    response = client.post('/api/receitas/', data=json.dumps(payload_receita_repasse), content_type='application/json')
    result = json.loads(response.content)

    assert result == ["Repasse não encontrado."]
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_receita_repasse_valor_diferente(
    client,
    tipo_receita,
    periodo,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    repasse,
    payload_receita_repasse
):
    with freeze_time('2019-11-29'):
        payload_receita_repasse['valor'] = 2000.67
        response = client.post('/api/receitas/', data=json.dumps(payload_receita_repasse),
                               content_type='application/json')
        result = json.loads(response.content)

        assert result == ['Valor do payload não é igual ao valor do CAPITAL.']
        assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_tabelas(
    jwt_authenticated_client,
    tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    detalhe_tipo_receita
):
    response = jwt_authenticated_client.get(f'/api/receitas/tabelas/?associacao_uuid={associacao.uuid}', content_type='application/json')
    result = json.loads(response.content)

    """
    'periodos': [{'data_fim_realizacao_despesas': '2019-08-31',
                  'data_inicio_realizacao_despesas': '2019-01-01',
                  'referencia': '2019.1',
                  'referencia_por_extenso': '1° repasse de 2019',
                  'uuid': '8022449b-86b4-4884-a431-6dd352be5c62'}],
    """

    esperado = {
        'tipos_receita': [
            {
                'id': tipo_receita.id,
                'nome': tipo_receita.nome,
                'e_repasse': tipo_receita.e_repasse,
                'aceita_capital': tipo_receita.aceita_capital,
                'aceita_custeio': tipo_receita.aceita_custeio,
                'aceita_livre': tipo_receita.aceita_livre,
                'e_devolucao': False,
                'detalhes_tipo_receita': [
                    {
                        'id': detalhe_tipo_receita.id,
                        'nome': detalhe_tipo_receita.nome
                    },
                ]
            },
        ],
        "categorias_receita": [
            {
                "id": "CAPITAL",
                "nome": "Capital"
            },
            {
                "id": "CUSTEIO",
                "nome": "Custeio"
            },
            {
                "id": "LIVRE",
                "nome": "Livre Aplicação"
            }
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
        ],

        'periodos': [
            {'data_fim_realizacao_despesas': '2019-08-31',
             'data_inicio_realizacao_despesas': '2019-01-01',
             'referencia': '2019.1',
             'referencia_por_extenso': '1° repasse de 2019',
             'uuid': str(associacao.periodo_inicial.uuid)
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_get_receitas(
    jwt_authenticated_client,
    tipo_receita,
    detalhe_tipo_receita,
    receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao):
    response = jwt_authenticated_client.get(f'/api/receitas/?associacao_uuid={associacao.uuid}', content_type='application/json')
    result = json.loads(response.content)

    results = [
        {
            'uuid': str(receita.uuid),
            'data': '2020-03-26',
            'valor': '100.00',
            'tipo_receita': {
                'id': tipo_receita.id,
                'nome': tipo_receita.nome,
                'e_repasse': tipo_receita.e_repasse,
                'aceita_capital': tipo_receita.aceita_capital,
                'aceita_custeio': tipo_receita.aceita_custeio,
                'aceita_livre': tipo_receita.aceita_livre,
                'e_devolucao': False,
            },
            'referencia_devolucao': None,
            "acao_associacao": {
                "uuid": str(acao_associacao.uuid),
                "id": acao_associacao.id,
                "nome": acao_associacao.acao.nome
            },
            'conta_associacao': {
                "uuid": str(conta_associacao.uuid),
                "nome": conta_associacao.tipo_conta.nome
            },
            'conferido': True,
            'categoria_receita': receita.categoria_receita,
            'detalhe_tipo_receita': {
                'id': detalhe_tipo_receita.id,
                'nome': detalhe_tipo_receita.nome
            },
            'detalhe_outros': receita.detalhe_outros,
            'notificar_dias_nao_conferido': 0
        },
    ]

    esperado = results

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_update_receita(
    jwt_authenticated_client,
    tipo_receita,
    detalhe_tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    receita,
    payload_receita
):
    response = jwt_authenticated_client.put(f'/api/receitas/{receita.uuid}/?associacao_uuid={associacao.uuid}', data=json.dumps(payload_receita),
                                            content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    receita = Receita.objects.get(uuid=result["uuid"])

    assert receita.associacao.uuid == associacao.uuid
    assert receita.detalhe_tipo_receita == detalhe_tipo_receita


def test_deleta_receita(
    jwt_authenticated_client,
    tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    receita,
    payload_receita):
    assert Receita.objects.filter(uuid=receita.uuid).exists()

    response = jwt_authenticated_client.delete(f'/api/receitas/{receita.uuid}/?associacao_uuid={associacao.uuid}', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Receita.objects.filter(uuid=receita.uuid).exists()


def test_deleta_receita_repasse(
    jwt_authenticated_client,
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

    response = jwt_authenticated_client.delete(f'/api/receitas/{receita_yyy_repasse.uuid}/?associacao_uuid={associacao.uuid}',
                                               content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Receita.objects.filter(uuid=receita_yyy_repasse.uuid).exists()

    assert Repasse.objects.get(uuid=repasse_realizado.uuid).status == 'PENDENTE'


def test_retrive_receitas(
    jwt_authenticated_client,
    tipo_receita,
    detalhe_tipo_receita,
    receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao):
    response = jwt_authenticated_client.get(f'/api/receitas/{receita.uuid}/?associacao_uuid={associacao.uuid}', content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'uuid': str(receita.uuid),
        'data': '2020-03-26',
        'valor': '100.00',
        'tipo_receita': {
            'id': tipo_receita.id,
            'nome': tipo_receita.nome,
            'e_repasse': tipo_receita.e_repasse,
            'aceita_capital': tipo_receita.aceita_capital,
            'aceita_custeio': tipo_receita.aceita_custeio,
            'aceita_livre': tipo_receita.aceita_livre,
            'e_devolucao': False,
        },
        'referencia_devolucao': None,
        "acao_associacao": {
            "uuid": str(acao_associacao.uuid),
            "id": acao_associacao.id,
            "nome": acao_associacao.acao.nome
        },
        'conta_associacao': {
            "uuid": str(conta_associacao.uuid),
            "nome": conta_associacao.tipo_conta.nome
        },
        'conferido': True,
        'categoria_receita': 'CUSTEIO',
        'detalhe_tipo_receita': {
            'id': detalhe_tipo_receita.id,
            'nome': detalhe_tipo_receita.nome
        },
        'detalhe_outros': receita.detalhe_outros,
        'notificar_dias_nao_conferido': 0
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_create_receita_livre_aplicacao(
    client,
    tipo_receita,
    detalhe_tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_receita_livre_aplicacao
):
    response = client.post('/api/receitas/', data=json.dumps(payload_receita_livre_aplicacao),
                           content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Receita.objects.filter(uuid=result["uuid"]).exists()

    receita = Receita.objects.get(uuid=result["uuid"])

    assert receita.associacao.uuid == associacao.uuid
    assert receita.detalhe_tipo_receita == detalhe_tipo_receita


def test_create_receita_repasse_livre_aplicacao(
    client,
    tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    repasse_2020_1_livre_aplicacao_pendente,
    payload_receita_repasse_livre_aplicacao
):
    with freeze_time('2020-03-29'):
        assert Repasse.objects.get(uuid=repasse_2020_1_livre_aplicacao_pendente.uuid).status == 'PENDENTE'

        response = client.post('/api/receitas/', data=json.dumps(payload_receita_repasse_livre_aplicacao),
                               content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED

        result = json.loads(response.content)

        assert Receita.objects.filter(uuid=result["uuid"]).exists()

        receita = Receita.objects.get(uuid=result["uuid"])

        assert receita.associacao.uuid == associacao.uuid

        assert Repasse.objects.get(uuid=repasse_2020_1_livre_aplicacao_pendente.uuid).status == 'REALIZADO'


@freeze_time('2020-03-29')
def test_create_receita_repasse_livre_aplicacao_valor_diferente(
    client,
    tipo_receita,
    periodo,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    repasse_2020_1_livre_aplicacao_pendente,
    payload_receita_repasse_livre_aplicacao
):

    payload_receita_repasse_livre_aplicacao['valor'] = 2000.67
    response = client.post('/api/receitas/', data=json.dumps(payload_receita_repasse_livre_aplicacao),
                           content_type='application/json')
    result = json.loads(response.content)

    assert result == ['Valor do payload não é igual ao valor do LIVRE.']
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_deleta_receita_repasse_livre_aplicacao(
    jwt_authenticated_client,
    tipo_receita_repasse,
    acao,
    acao_associacao_role_cultural,
    associacao,
    tipo_conta_cartao,
    conta_associacao_cartao,
    receita_repasse_livre_aplicacao,
    repasse_realizado_livre_aplicacao
):
    assert Repasse.objects.get(uuid=repasse_realizado_livre_aplicacao.uuid).status == 'REALIZADO'

    assert Receita.objects.filter(uuid=receita_repasse_livre_aplicacao.uuid).exists()

    response = jwt_authenticated_client.delete(f'/api/receitas/{receita_repasse_livre_aplicacao.uuid}/?associacao_uuid={associacao.uuid}',
                                               content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Receita.objects.filter(uuid=receita_repasse_livre_aplicacao.uuid).exists()

    assert Repasse.objects.get(uuid=repasse_realizado_livre_aplicacao.uuid).status == 'PENDENTE'
