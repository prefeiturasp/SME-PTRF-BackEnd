import datetime
import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def despesa_teste_ordenar_01(
    associacao,
    tipo_documento,
    tipo_transacao,
):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 10),
        valor_total=100.00,
    )


@pytest.fixture
def despesa_teste_ordenar_02(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='654321',
        data_documento=datetime.date(2020, 3, 11),
        valor_total=200.00,
    )


@pytest.fixture
def despesa_teste_ordenar_03(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='777777',
        data_documento=datetime.date(2020, 3, 15),
        valor_total=60.00,
    )


@pytest.fixture
def despesa_teste_ordenar_04(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='888888',
        data_documento=datetime.date(2020, 3, 16),
        valor_total=50.00,
    )

@pytest.fixture
def despesa_teste_ordenar_05(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='888888',
        data_documento=datetime.date(2020, 3, 13),
        valor_total=70.00,
    )


@pytest.fixture
def despesa_teste_ordenar_06(
    associacao,
    tipo_documento,
    tipo_transacao,
    despesa_teste_ordenar_07,
    despesa_teste_ordenar_08,
):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 10),
        valor_total=100.00,
        retem_imposto=True,
        despesas_impostos=[despesa_teste_ordenar_07, despesa_teste_ordenar_08]
    )


@pytest.fixture
def despesa_teste_ordenar_07(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='654321',
        data_documento=datetime.date(2020, 3, 11),
        valor_total=200.00,
    )


@pytest.fixture
def despesa_teste_ordenar_08(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='',
        data_documento=datetime.date(2020, 3, 15),
        valor_total=60.00,
    )


@pytest.fixture
def despesa_teste_ordenar_09(associacao, tipo_documento, tipo_transacao, despesa_teste_ordenar_10):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='888888',
        data_documento=datetime.date(2020, 3, 16),
        valor_total=50.00,
        retem_imposto=True,
        despesas_impostos=[despesa_teste_ordenar_10]
    )

@pytest.fixture
def despesa_teste_ordenar_10(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='888888',
        data_documento=datetime.date(2020, 3, 13),
        valor_total=70.00,
    )


def test_api_ordenar_despesa_por_numero_do_documento_crescente(
    jwt_authenticated_client_d,
    associacao,
    despesa_teste_ordenar_01,
    despesa_teste_ordenar_02
):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?associacao__uuid={associacao.uuid}&ordenar_por_numero_do_documento=crescente',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert result[0]['numero_documento'] == '123456'
    assert result[1]['numero_documento'] == '654321'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_despesa_por_numero_do_documento_decrescente(
    jwt_authenticated_client_d,
    associacao,
    despesa_teste_ordenar_01,
    despesa_teste_ordenar_02
):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?associacao__uuid={associacao.uuid}&ordenar_por_numero_do_documento=decrescente',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert result[0]['numero_documento'] == '654321'
    assert result[1]['numero_documento'] == '123456'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_despesa_por_data_documento_crescente(
    jwt_authenticated_client_d,
    associacao,
    despesa_teste_ordenar_01,
    despesa_teste_ordenar_02
):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?associacao__uuid={associacao.uuid}&ordenar_por_data_especificacao=crescente',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert result[0]['data_documento'] == '2020-03-10'
    assert result[1]['data_documento'] == '2020-03-11'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_despesa_por_data_documento_decrescente(
    jwt_authenticated_client_d,
    associacao,
    despesa_teste_ordenar_01,
    despesa_teste_ordenar_02
):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?associacao__uuid={associacao.uuid}&ordenar_por_data_especificacao=decrescente',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert result[0]['data_documento'] == '2020-03-11'
    assert result[1]['data_documento'] == '2020-03-10'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_despesa_por_valor_crescente(
    jwt_authenticated_client_d,
    associacao,
    despesa_teste_ordenar_01,
    despesa_teste_ordenar_02
):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?associacao__uuid={associacao.uuid}&ordenar_por_valor=crescente',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert result[0]['valor_total'] == '100.00'
    assert result[1]['valor_total'] == '200.00'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_despesa_por_valor_decrescente(
    jwt_authenticated_client_d,
    associacao,
    despesa_teste_ordenar_01,
    despesa_teste_ordenar_02
):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?associacao__uuid={associacao.uuid}&ordenar_por_valor=decrescente',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert result[0]['valor_total'] == '200.00'
    assert result[1]['valor_total'] == '100.00'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_despesa_por_numero_documento_crescente_e_data_crescente(
    jwt_authenticated_client_d,
    associacao,
    despesa_teste_ordenar_03,
    despesa_teste_ordenar_04,
    despesa_teste_ordenar_05,
):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?associacao__uuid={associacao.uuid}&ordenar_por_numero_do_documento=crescente&ordenar_por_data_especificacao=crescente',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert result[0]['numero_documento'] == '777777'
    assert result[0]['valor_total'] == '60.00'
    assert result[0]['data_documento'] == '2020-03-15'

    assert result[1]['numero_documento'] == '888888'
    assert result[1]['valor_total'] == '70.00'
    assert result[1]['data_documento'] == '2020-03-13'

    assert result[2]['numero_documento'] == '888888'
    assert result[2]['valor_total'] == '50.00'
    assert result[2]['data_documento'] == '2020-03-16'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_despesa_por_numero_documento_decrescente_e_data_crescente(
    jwt_authenticated_client_d,
    associacao,
    despesa_teste_ordenar_03,
    despesa_teste_ordenar_04,
    despesa_teste_ordenar_05,
):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?associacao__uuid={associacao.uuid}&ordenar_por_numero_do_documento=decrescente&ordenar_por_data_especificacao=crescente',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert result[0]['numero_documento'] == '888888'
    assert result[0]['valor_total'] == '70.00'
    assert result[0]['data_documento'] == '2020-03-13'

    assert result[1]['numero_documento'] == '888888'
    assert result[1]['valor_total'] == '50.00'
    assert result[1]['data_documento'] == '2020-03-16'

    assert result[2]['numero_documento'] == '777777'
    assert result[2]['valor_total'] == '60.00'
    assert result[2]['data_documento'] == '2020-03-15'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_despesa_por_numero_documento_decrescente_e_data_decrescente(
    jwt_authenticated_client_d,
    associacao,
    despesa_teste_ordenar_03,
    despesa_teste_ordenar_04,
    despesa_teste_ordenar_05,
):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?associacao__uuid={associacao.uuid}&ordenar_por_numero_do_documento=decrescente&ordenar_por_data_especificacao=decrescente',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert result[0]['numero_documento'] == '888888'
    assert result[0]['valor_total'] == '50.00'
    assert result[0]['data_documento'] == '2020-03-16'

    assert result[1]['numero_documento'] == '888888'
    assert result[1]['valor_total'] == '70.00'
    assert result[1]['data_documento'] == '2020-03-13'

    assert result[2]['numero_documento'] == '777777'
    assert result[2]['valor_total'] == '60.00'
    assert result[2]['data_documento'] == '2020-03-15'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_despesa_por_imposto(
    jwt_authenticated_client_d,
    associacao,
    despesa_teste_ordenar_06,
    despesa_teste_ordenar_07,
    despesa_teste_ordenar_08,
    despesa_teste_ordenar_09,
    despesa_teste_ordenar_10,
):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?associacao__uuid={associacao.uuid}&ordenar_por_imposto=true',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert result[0]['numero_documento'] == '123456'
    assert result[0]['valor_total'] == '100.00'
    assert result[0]['data_documento'] == '2020-03-10'

    assert result[1]['numero_documento'] == '654321'
    assert result[1]['valor_total'] == '200.00'
    assert result[1]['data_documento'] == '2020-03-11'

    assert result[2]['numero_documento'] == ''
    assert result[2]['valor_total'] == '60.00'
    assert result[2]['data_documento'] == '2020-03-15'

    assert result[3]['numero_documento'] == '888888'
    assert result[3]['valor_total'] == '50.00'
    assert result[3]['data_documento'] == '2020-03-16'

    assert result[4]['numero_documento'] == '888888'
    assert result[4]['valor_total'] == '70.00'
    assert result[4]['data_documento'] == '2020-03-13'

    assert response.status_code == status.HTTP_200_OK



