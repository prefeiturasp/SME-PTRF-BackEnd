import datetime
import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_despesas_filtro_por_tipo_aplicacao(jwt_authenticated_client, associacao, despesa, conta_associacao,
                                                    acao,
                                                    tipo_aplicacao_recurso_custeio,
                                                    tipo_custeio_servico,
                                                    especificacao_instalacao_eletrica,
                                                    acao_associacao_ptrf,
                                                    acao_associacao_role_cultural,
                                                    especificacao_material_eletrico,
                                                    especificacao_ar_condicionado,
                                                    rateio_despesa_material_eletrico_role_cultural,
                                                    rateio_despesa_instalacao_eletrica_ptrf,
                                                    rateio_despesa_ar_condicionado_ptrf):
    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&aplicacao_recurso=CUSTEIO',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2

    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&aplicacao_recurso=CAPITAL',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_api_get_despesas_filtro_por_acao_associacao(jwt_authenticated_client, associacao, despesa, conta_associacao,
                                                     acao,
                                                     tipo_aplicacao_recurso_custeio,
                                                     tipo_custeio_servico,
                                                     especificacao_instalacao_eletrica,
                                                     acao_associacao_ptrf,
                                                     acao_associacao_role_cultural,
                                                     especificacao_material_eletrico,
                                                     especificacao_ar_condicionado,
                                                     rateio_despesa_material_eletrico_role_cultural,
                                                     rateio_despesa_instalacao_eletrica_ptrf,
                                                     rateio_despesa_ar_condicionado_ptrf):
    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&acao_associacao__uuid={acao_associacao_ptrf.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2

    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&acao_associacao__uuid={acao_associacao_role_cultural.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


@pytest.fixture
def despesa_incompleta(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=None,
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=None,
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_capital_completo(associacao, despesa_incompleta, conta_associacao, acao,
                                    tipo_aplicacao_recurso_capital,
                                    especificacao_material_servico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_incompleta,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
        especificacao_material_servico=especificacao_material_servico,
        valor_rateio=10.00,  # Falta o valor
        quantidade_itens_capital=1,
        valor_item_capital=10.00,
        numero_processo_incorporacao_capital='teste123456'
    )


@pytest.fixture
def rateio_despesa_capital_incompleto(associacao, despesa_incompleta, conta_associacao, acao,
                                      tipo_aplicacao_recurso_capital,
                                      especificacao_material_servico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_incompleta,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
        especificacao_material_servico=especificacao_material_servico,
        valor_rateio=0.00,
        quantidade_itens_capital=0,
        valor_item_capital=0,
        numero_processo_incorporacao_capital=''
    )


@pytest.fixture
def rateio_despesa_custeio_completo(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso_custeio,
                                    tipo_custeio_servico, especificacao_material_servico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_material_servico,
        valor_rateio=100.00,

    )


def test_api_get_despesas_filtro_por_status(jwt_authenticated_client, associacao, despesa_incompleta,
                                            rateio_despesa_capital_completo,
                                            rateio_despesa_capital_incompleto, despesa,
                                            rateio_despesa_custeio_completo):
    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&despesa__status=COMPLETO',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&despesa__status=INCOMPLETO',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2


@pytest.fixture
def _rateio_despesa_conferido(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso, tipo_custeio,
                             especificacao_material_servico, acao_associacao, periodo_2020_1):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso,
        tipo_custeio=tipo_custeio,
        especificacao_material_servico=especificacao_material_servico,
        valor_rateio=100.00,
        quantidade_itens_capital=2,
        valor_item_capital=50.00,
        numero_processo_incorporacao_capital='Teste123456',
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2020_1,
        valor_original=90.00,
    )


@pytest.fixture
def _rateio_despesa_nao_conferido(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso, tipo_custeio,
                                 especificacao_material_servico, acao_associacao, periodo_2020_1):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso,
        tipo_custeio=tipo_custeio,
        especificacao_material_servico=especificacao_material_servico,
        valor_rateio=100.00,
        quantidade_itens_capital=2,
        valor_item_capital=50.00,
        numero_processo_incorporacao_capital='Teste123456',
        update_conferido=True,
        conferido=False,
        periodo_conciliacao=periodo_2020_1,
        valor_original=90.00,
    )


def test_api_get_despesas_filtro_por_conferido(jwt_authenticated_client, associacao, despesa,
                                               _rateio_despesa_conferido,
                                               _rateio_despesa_nao_conferido):
    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&conferido=True',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_api_get_despesas_filtro_por_nao_conferido(jwt_authenticated_client, associacao, despesa,
                                                   rateio_despesa_conferido,
                                                   rateio_despesa_nao_conferido,
                                                   rateio_despesa_nao_conferido2):
    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&conferido=False',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2


@pytest.fixture
def despesa_2020_3_10(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_2020_3_10(associacao, despesa_2020_3_10, conta_associacao, acao, tipo_aplicacao_recurso_custeio,
                             tipo_custeio_servico,
                             especificacao_instalacao_eletrica, acao_associacao_ptrf):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2020_3_10,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        conferido=True,

    )


@pytest.fixture
def despesa_2020_3_11(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 11),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 11),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_2020_3_11(associacao, despesa_2020_3_11, conta_associacao, acao, tipo_aplicacao_recurso_custeio,
                             tipo_custeio_servico,
                             especificacao_instalacao_eletrica, acao_associacao_ptrf):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2020_3_11,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        conferido=True,

    )


def test_api_get_despesas_filtro_por_periodo(jwt_authenticated_client, associacao, despesa_2020_3_10,
                                             rateio_despesa_2020_3_10, despesa_2020_3_11, rateio_despesa_2020_3_11):
    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&data_inicio=2020-03-10&data_fim=2020-03-10',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&data_inicio=2020-03-10&data_fim=2020-03-11',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2

    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&data_inicio=2020-03-01&data_fim=2020-03-09',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 0


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
def rateio_despesa_fornecedor_a(associacao, despesa_fornecedor_a, conta_associacao, acao,
                                tipo_aplicacao_recurso_custeio,
                                tipo_custeio_servico,
                                especificacao_instalacao_eletrica, acao_associacao_ptrf):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_fornecedor_a,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        conferido=True,

    )


@pytest.fixture
def despesa_fornecedor_b(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 11),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor B Graca valença',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 11),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_fornecedor_b(associacao, despesa_fornecedor_b, conta_associacao, acao,
                                tipo_aplicacao_recurso_custeio,
                                tipo_custeio_servico,
                                especificacao_instalacao_eletrica, acao_associacao_ptrf):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_fornecedor_b,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        conferido=True,

    )


def test_api_get_despesas_filtro_por_fornecedor(jwt_authenticated_client, associacao, despesa_fornecedor_a,
                                                rateio_despesa_fornecedor_a, despesa_fornecedor_b,
                                                rateio_despesa_fornecedor_b):
    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&fornecedor=dor a',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1, 'Deve localizar por qualquer parte do nome. Case insensitive.'

    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&fornecedor=graca',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2, 'Deve desconsiderar caracteres especiais'

    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&fornecedor=xpto',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 0

    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&fornecedor=VALENCA',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1, 'Deve ignorar acentos e ser case insensitive.'

    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&fornecedor=árvore',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1, 'Deve ignorar acentos e ser case insensitive.'
