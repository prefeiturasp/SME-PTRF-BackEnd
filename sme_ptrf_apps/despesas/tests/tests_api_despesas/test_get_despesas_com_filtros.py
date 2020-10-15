import datetime
import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def despesa_fornecedor_a(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor A graça ARVORE',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def despesa_fornecedor_b(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='654321',
        data_documento=datetime.date(2020, 3, 11),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='517.870.110-03',
        nome_fornecedor='Fornecedor B Graca valença',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 11),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


def test_api_get_despesas_filtro_por_cnpj_cpf_fornecedor(jwt_authenticated_client, associacao, despesa_fornecedor_a,
                                                         despesa_fornecedor_b):
    response = jwt_authenticated_client.get(
        f'/api/despesas/?associacao__uuid={associacao.uuid}&cpf_cnpj_fornecedor=11.478.276/0001-04',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1, 'Deve localizar pelo CNPJ.'

    response = jwt_authenticated_client.get(
        f'/api/despesas/?associacao__uuid={associacao.uuid}&cpf_cnpj_fornecedor=517.870.110-03',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1, 'Deve localizar pelo CPF'

    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&cpf_cnpj_fornecedor=343646',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 0, 'Não deveria ter achado nada'


def test_api_get_despesas_filtro_por_tipo_documento(jwt_authenticated_client, associacao, despesa_fornecedor_a,
                                                    despesa_fornecedor_b, tipo_documento):
    response = jwt_authenticated_client.get(
        f'/api/despesas/?tipo_documento__uuid={tipo_documento.uuid}', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2, 'Deve localizar pelo Tipo de documento.'

    response = jwt_authenticated_client.get(
        f'/api/despesas/?tipo_documento__uuid={despesa_fornecedor_b.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 0, 'Não deveria ter achado nada'


def test_api_get_despesas_filtro_por_numero_documento(jwt_authenticated_client, associacao, despesa_fornecedor_a,
                                                      despesa_fornecedor_b, tipo_documento):
    response = jwt_authenticated_client.get(
        f'/api/despesas/?numero_documento=123456', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1, 'Deve localizar pelo número do documento.'

    response = jwt_authenticated_client.get(
        f'/api/despesas/?numero_documento=999999',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 0, 'Não deveria ter achado nada'


def test_api_get_despesas_campos(jwt_authenticated_client, associacao, despesa_fornecedor_a,
                                 despesa_fornecedor_b, tipo_documento):
    response = jwt_authenticated_client.get(
        f'/api/despesas/?numero_documento=123456', content_type='application/json')
    result = json.loads(response.content)

    esperado = [
        {
            'associacao': f'{associacao.uuid}',
            'cpf_cnpj_fornecedor': '11.478.276/0001-04',
            'data_documento': '2020-03-10',
            'nome_fornecedor': 'Fornecedor A graça ARVORE',
            'numero_documento': '123456',
            'tipo_documento': {
                'id': tipo_documento.id,
                'nome': 'NFe',
            },
            'uuid': f'{despesa_fornecedor_a.uuid}',
            'valor_ptrf': 90.0,
            'valor_total': '100.00'
        }
    ]
    assert response.status_code == status.HTTP_200_OK
    assert result == esperado, 'Não retornou o esperado.'
