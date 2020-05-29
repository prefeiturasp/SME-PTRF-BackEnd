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


def test_api_get_despesas_filtro_por_conferido(jwt_authenticated_client, associacao, despesa,
                                               rateio_despesa_conferido,
                                               rateio_despesa_nao_conferido,
                                               rateio_despesa_nao_conferido2):
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
