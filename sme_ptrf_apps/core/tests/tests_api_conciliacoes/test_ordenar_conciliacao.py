import datetime
import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def despesa_conciliacao_teste_ordenar_01(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2019, 6, 2),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2019, 6, 2),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_conciliacao_teste_ordenar_01(associacao, despesa_conciliacao_teste_ordenar_01,
                                                conta_associacao_cartao, acao,
                                                tipo_aplicacao_recurso_custeio,
                                                tipo_custeio_servico,
                                                especificacao_instalacao_eletrica, acao_associacao_role_cultural,
                                                periodo_2019_2):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_conciliacao_teste_ordenar_01,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2019_2

    )


@pytest.fixture
def despesa_conciliacao_teste_ordenar_02(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='654321',
        data_documento=datetime.date(2019, 6, 3),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2019, 6, 2),
        valor_total=200.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_conciliacao_teste_ordenar_02(associacao, despesa_conciliacao_teste_ordenar_02,
                                                conta_associacao_cartao, acao,
                                                tipo_aplicacao_recurso_custeio,
                                                tipo_custeio_servico,
                                                especificacao_instalacao_eletrica, acao_associacao_role_cultural,
                                                periodo_2019_2):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_conciliacao_teste_ordenar_02,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=200.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2019_2

    )


@pytest.fixture
def despesa_conciliacao_teste_ordenar_03(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='777777',
        data_documento=datetime.date(2019, 6, 15),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2019, 6, 2),
        valor_total=60.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_conciliacao_teste_ordenar_03(associacao, despesa_conciliacao_teste_ordenar_03,
                                                conta_associacao_cartao, acao,
                                                tipo_aplicacao_recurso_custeio,
                                                tipo_custeio_servico,
                                                especificacao_instalacao_eletrica, acao_associacao_role_cultural,
                                                periodo_2019_2):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_conciliacao_teste_ordenar_03,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=60.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2019_2

    )


@pytest.fixture
def despesa_conciliacao_teste_ordenar_04(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='888888',
        data_documento=datetime.date(2019, 6, 16),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2019, 6, 2),
        valor_total=50.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_conciliacao_teste_ordenar_04(associacao, despesa_conciliacao_teste_ordenar_04,
                                                conta_associacao_cartao, acao,
                                                tipo_aplicacao_recurso_custeio,
                                                tipo_custeio_servico,
                                                especificacao_instalacao_eletrica, acao_associacao_role_cultural,
                                                periodo_2019_2):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_conciliacao_teste_ordenar_04,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=50.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2019_2

    )


@pytest.fixture
def despesa_conciliacao_teste_ordenar_05(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='888888',
        data_documento=datetime.date(2019, 6, 13),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2019, 6, 2),
        valor_total=70.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_conciliacao_teste_ordenar_05(associacao, despesa_conciliacao_teste_ordenar_05,
                                                conta_associacao_cartao, acao,
                                                tipo_aplicacao_recurso_custeio,
                                                tipo_custeio_servico,
                                                especificacao_instalacao_eletrica, acao_associacao_role_cultural,
                                                periodo_2019_2):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_conciliacao_teste_ordenar_05,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=70.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2019_2

    )


@pytest.fixture
def despesa_conciliacao_teste_ordenar_06(
    associacao, tipo_documento, tipo_transacao,
    despesa_conciliacao_teste_ordenar_07, despesa_conciliacao_teste_ordenar_08
):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2019, 6, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2019, 6, 2),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
        despesas_impostos=[despesa_conciliacao_teste_ordenar_07, despesa_conciliacao_teste_ordenar_08],
        retem_imposto=True
    )


@pytest.fixture
def rateio_despesa_conciliacao_teste_ordenar_06(associacao, despesa_conciliacao_teste_ordenar_06,
                                                conta_associacao_cartao, acao,
                                                tipo_aplicacao_recurso_custeio,
                                                tipo_custeio_servico,
                                                especificacao_instalacao_eletrica, acao_associacao_role_cultural,
                                                periodo_2019_2):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_conciliacao_teste_ordenar_06,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2019_2

    )


@pytest.fixture
def despesa_conciliacao_teste_ordenar_07(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='654321',
        data_documento=datetime.date(2019, 6, 11),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2019, 6, 2),
        valor_total=200.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_conciliacao_teste_ordenar_07(associacao, despesa_conciliacao_teste_ordenar_07,
                                                conta_associacao_cartao, acao,
                                                tipo_aplicacao_recurso_custeio,
                                                tipo_custeio_servico,
                                                especificacao_instalacao_eletrica, acao_associacao_role_cultural,
                                                periodo_2019_2):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_conciliacao_teste_ordenar_07,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=200.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2019_2

    )


@pytest.fixture
def despesa_conciliacao_teste_ordenar_08(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='',
        data_documento=datetime.date(2019, 6, 15),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2019, 6, 2),
        valor_total=60.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_conciliacao_teste_ordenar_08(associacao, despesa_conciliacao_teste_ordenar_08,
                                                conta_associacao_cartao, acao,
                                                tipo_aplicacao_recurso_custeio,
                                                tipo_custeio_servico,
                                                especificacao_instalacao_eletrica, acao_associacao_role_cultural,
                                                periodo_2019_2):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_conciliacao_teste_ordenar_08,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=60.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2019_2

    )


@pytest.fixture
def despesa_conciliacao_teste_ordenar_09(
    associacao, tipo_documento, tipo_transacao, despesa_conciliacao_teste_ordenar_10
):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='888888',
        data_documento=datetime.date(2019, 6, 16),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2019, 6, 2),
        valor_total=50.00,
        valor_recursos_proprios=10.00,
        despesas_impostos=[despesa_conciliacao_teste_ordenar_10],
        retem_imposto=True
    )


@pytest.fixture
def rateio_despesa_conciliacao_teste_ordenar_09(associacao, despesa_conciliacao_teste_ordenar_09,
                                                conta_associacao_cartao, acao,
                                                tipo_aplicacao_recurso_custeio,
                                                tipo_custeio_servico,
                                                especificacao_instalacao_eletrica, acao_associacao_role_cultural,
                                                periodo_2019_2):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_conciliacao_teste_ordenar_09,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=50.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2019_2

    )


@pytest.fixture
def despesa_conciliacao_teste_ordenar_10(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='888888',
        data_documento=datetime.date(2019, 6, 13),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2019, 6, 2),
        valor_total=70.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_conciliacao_teste_ordenar_10(associacao, despesa_conciliacao_teste_ordenar_10,
                                                conta_associacao_cartao, acao,
                                                tipo_aplicacao_recurso_custeio,
                                                tipo_custeio_servico,
                                                especificacao_instalacao_eletrica, acao_associacao_role_cultural,
                                                periodo_2019_2):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_conciliacao_teste_ordenar_10,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=70.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2019_2

    )


def test_api_ordenar_conciliacao_por_numero_do_documento_crescente(
    jwt_authenticated_client_a,
    associacao,
    despesa_conciliacao_teste_ordenar_01,
    rateio_despesa_conciliacao_teste_ordenar_01,
    despesa_conciliacao_teste_ordenar_02,
    rateio_despesa_conciliacao_teste_ordenar_02,
    periodo_2019_2,
    conta_associacao_cartao,
):

    url = f'/api/conciliacoes/transacoes-despesa/?periodo={periodo_2019_2.uuid}' \
          f'&conta_associacao={conta_associacao_cartao.uuid}&conferido=True&ordenar_por_numero_do_documento=crescente'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert result[0]['numero_documento'] == '123456'
    assert result[1]['numero_documento'] == '654321'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_conciliacao_por_numero_do_documento_decrescente(
    jwt_authenticated_client_a,
    associacao,
    despesa_conciliacao_teste_ordenar_01,
    rateio_despesa_conciliacao_teste_ordenar_01,
    despesa_conciliacao_teste_ordenar_02,
    rateio_despesa_conciliacao_teste_ordenar_02,
    periodo_2019_2,
    conta_associacao_cartao,
):

    url = f'/api/conciliacoes/transacoes-despesa/?periodo={periodo_2019_2.uuid}' \
          f'&conta_associacao={conta_associacao_cartao.uuid}&conferido=True&ordenar_por_numero_do_documento=decrescente'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert result[0]['numero_documento'] == '654321'
    assert result[1]['numero_documento'] == '123456'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_conciliacao_por_data_documento_crescente(
    jwt_authenticated_client_a,
    associacao,
    despesa_conciliacao_teste_ordenar_01,
    rateio_despesa_conciliacao_teste_ordenar_01,
    despesa_conciliacao_teste_ordenar_02,
    rateio_despesa_conciliacao_teste_ordenar_02,
    periodo_2019_2,
    conta_associacao_cartao,
):
    url = f'/api/conciliacoes/transacoes-despesa/?periodo={periodo_2019_2.uuid}' \
          f'&conta_associacao={conta_associacao_cartao.uuid}&conferido=True&ordenar_por_data_especificacao=crescente'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert result[0]['documento_mestre']['data_documento'] == '2019-06-02'
    assert result[1]['documento_mestre']['data_documento'] == '2019-06-03'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_conciliacao_por_data_documento_decrescente(
    jwt_authenticated_client_a,
    associacao,
    despesa_conciliacao_teste_ordenar_01,
    rateio_despesa_conciliacao_teste_ordenar_01,
    despesa_conciliacao_teste_ordenar_02,
    rateio_despesa_conciliacao_teste_ordenar_02,
    periodo_2019_2,
    conta_associacao_cartao,
):
    url = f'/api/conciliacoes/transacoes-despesa/?periodo={periodo_2019_2.uuid}' \
          f'&conta_associacao={conta_associacao_cartao.uuid}&conferido=True&ordenar_por_data_especificacao=decrescente'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert result[0]['documento_mestre']['data_documento'] == '2019-06-03'
    assert result[1]['documento_mestre']['data_documento'] == '2019-06-02'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_conciliacao_por_valor_crescente(
    jwt_authenticated_client_a,
    associacao,
    despesa_conciliacao_teste_ordenar_01,
    rateio_despesa_conciliacao_teste_ordenar_01,
    despesa_conciliacao_teste_ordenar_02,
    rateio_despesa_conciliacao_teste_ordenar_02,
    periodo_2019_2,
    conta_associacao_cartao,
):
    url = f'/api/conciliacoes/transacoes-despesa/?periodo={periodo_2019_2.uuid}' \
          f'&conta_associacao={conta_associacao_cartao.uuid}&conferido=True&ordenar_por_valor=crescente'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert result[0]['documento_mestre']['valor_total'] == '100.00'
    assert result[1]['documento_mestre']['valor_total'] == '200.00'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_conciliacao_por_valor_decrescente(
    jwt_authenticated_client_a,
    associacao,
    despesa_conciliacao_teste_ordenar_01,
    rateio_despesa_conciliacao_teste_ordenar_01,
    despesa_conciliacao_teste_ordenar_02,
    rateio_despesa_conciliacao_teste_ordenar_02,
    periodo_2019_2,
    conta_associacao_cartao,
):
    url = f'/api/conciliacoes/transacoes-despesa/?periodo={periodo_2019_2.uuid}' \
          f'&conta_associacao={conta_associacao_cartao.uuid}&conferido=True&ordenar_por_valor=decrescente'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert result[0]['documento_mestre']['valor_total'] == '200.00'
    assert result[1]['documento_mestre']['valor_total'] == '100.00'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_conciliacao_por_numero_documento_crescente_e_data_crescente(
    jwt_authenticated_client_a,
    associacao,
    despesa_conciliacao_teste_ordenar_03,
    rateio_despesa_conciliacao_teste_ordenar_03,
    despesa_conciliacao_teste_ordenar_04,
    rateio_despesa_conciliacao_teste_ordenar_04,
    despesa_conciliacao_teste_ordenar_05,
    rateio_despesa_conciliacao_teste_ordenar_05,
    periodo_2019_2,
    conta_associacao_cartao,
):
    url = f'/api/conciliacoes/transacoes-despesa/?periodo={periodo_2019_2.uuid}' \
          f'&conta_associacao={conta_associacao_cartao.uuid}&conferido=True' \
          f'&ordenar_por_numero_do_documento=crescente&ordenar_por_data_especificacao=crescente'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert result[0]['numero_documento'] == '777777'
    assert result[0]['documento_mestre']['valor_total'] == '60.00'
    assert result[0]['documento_mestre']['data_documento'] == '2019-06-15'

    assert result[1]['numero_documento'] == '888888'
    assert result[1]['documento_mestre']['valor_total'] == '70.00'
    assert result[1]['documento_mestre']['data_documento'] == '2019-06-13'

    assert result[2]['numero_documento'] == '888888'
    assert result[2]['documento_mestre']['valor_total'] == '50.00'
    assert result[2]['documento_mestre']['data_documento'] == '2019-06-16'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_conciliacao_por_numero_documento_decrescente_e_data_crescente(
    jwt_authenticated_client_a,
    associacao,
    despesa_conciliacao_teste_ordenar_03,
    rateio_despesa_conciliacao_teste_ordenar_03,
    despesa_conciliacao_teste_ordenar_04,
    rateio_despesa_conciliacao_teste_ordenar_04,
    despesa_conciliacao_teste_ordenar_05,
    rateio_despesa_conciliacao_teste_ordenar_05,
    periodo_2019_2,
    conta_associacao_cartao,
):
    url = f'/api/conciliacoes/transacoes-despesa/?periodo={periodo_2019_2.uuid}' \
          f'&conta_associacao={conta_associacao_cartao.uuid}&conferido=True' \
          f'&ordenar_por_numero_do_documento=decrescente&ordenar_por_data_especificacao=crescente'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert result[0]['numero_documento'] == '888888'
    assert result[0]['documento_mestre']['valor_total'] == '70.00'
    assert result[0]['documento_mestre']['data_documento'] == '2019-06-13'

    assert result[1]['numero_documento'] == '888888'
    assert result[1]['documento_mestre']['valor_total'] == '50.00'
    assert result[1]['documento_mestre']['data_documento'] == '2019-06-16'

    assert result[2]['numero_documento'] == '777777'
    assert result[2]['documento_mestre']['valor_total'] == '60.00'
    assert result[2]['documento_mestre']['data_documento'] == '2019-06-15'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_conciliacao_por_numero_documento_decrescente_e_data_decrescente(
    jwt_authenticated_client_a,
    associacao,
    despesa_conciliacao_teste_ordenar_03,
    rateio_despesa_conciliacao_teste_ordenar_03,
    despesa_conciliacao_teste_ordenar_04,
    rateio_despesa_conciliacao_teste_ordenar_04,
    despesa_conciliacao_teste_ordenar_05,
    rateio_despesa_conciliacao_teste_ordenar_05,
    periodo_2019_2,
    conta_associacao_cartao,
):
    url = f'/api/conciliacoes/transacoes-despesa/?periodo={periodo_2019_2.uuid}' \
          f'&conta_associacao={conta_associacao_cartao.uuid}&conferido=True' \
          f'&ordenar_por_numero_do_documento=decrescente&ordenar_por_data_especificacao=decrescente'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert result[0]['numero_documento'] == '888888'
    assert result[0]['documento_mestre']['valor_total'] == '50.00'
    assert result[0]['documento_mestre']['data_documento'] == '2019-06-16'

    assert result[1]['numero_documento'] == '888888'
    assert result[1]['documento_mestre']['valor_total'] == '70.00'
    assert result[1]['documento_mestre']['data_documento'] == '2019-06-13'

    assert result[2]['numero_documento'] == '777777'
    assert result[2]['documento_mestre']['valor_total'] == '60.00'
    assert result[2]['documento_mestre']['data_documento'] == '2019-06-15'

    assert response.status_code == status.HTTP_200_OK


def test_api_ordenar_conciliacao_por_imposto(
    jwt_authenticated_client_a,
    associacao,
    despesa_conciliacao_teste_ordenar_06,
    rateio_despesa_conciliacao_teste_ordenar_06,
    despesa_conciliacao_teste_ordenar_07,
    rateio_despesa_conciliacao_teste_ordenar_07,
    despesa_conciliacao_teste_ordenar_08,
    rateio_despesa_conciliacao_teste_ordenar_08,
    despesa_conciliacao_teste_ordenar_09,
    rateio_despesa_conciliacao_teste_ordenar_09,
    despesa_conciliacao_teste_ordenar_10,
    rateio_despesa_conciliacao_teste_ordenar_10,
    periodo_2019_2,
    conta_associacao_cartao,
):
    url = f'/api/conciliacoes/transacoes-despesa/?periodo={periodo_2019_2.uuid}' \
          f'&conta_associacao={conta_associacao_cartao.uuid}&conferido=True' \
          f'&ordenar_por_imposto=true'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert result[0]['numero_documento'] == '123456'
    assert result[0]['documento_mestre']['valor_total'] == '100.00'
    assert result[0]['documento_mestre']['data_documento'] == '2019-06-10'

    assert result[1]['numero_documento'] == '654321'
    assert result[1]['documento_mestre']['valor_total'] == '200.00'
    assert result[1]['documento_mestre']['data_documento'] == '2019-06-11'

    assert result[2]['numero_documento'] == ''
    assert result[2]['documento_mestre']['valor_total'] == '60.00'
    assert result[2]['documento_mestre']['data_documento'] == '2019-06-15'

    assert result[3]['numero_documento'] == '888888'
    assert result[3]['documento_mestre']['valor_total'] == '50.00'
    assert result[3]['documento_mestre']['data_documento'] == '2019-06-16'

    assert result[4]['numero_documento'] == '888888'
    assert result[4]['documento_mestre']['valor_total'] == '70.00'
    assert result[4]['documento_mestre']['data_documento'] == '2019-06-13'

    assert response.status_code == status.HTTP_200_OK
