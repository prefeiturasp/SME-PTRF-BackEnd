import json
import pytest

from datetime import date

from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_despesas_totais_filtro_por_tipo_aplicacao(jwt_authenticated_client_d, associacao, despesa,
                                                           conta_associacao,
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
    response = jwt_authenticated_client_d.get(
        f'/api/rateios-despesas/totais/?associacao__uuid={associacao.uuid}&aplicacao_recurso=CUSTEIO',
        content_type='application/json')
    result = json.loads(response.content)

    total_despesas_sem_filtro = rateio_despesa_material_eletrico_role_cultural.valor_rateio + \
                                rateio_despesa_instalacao_eletrica_ptrf.valor_rateio + \
                                rateio_despesa_ar_condicionado_ptrf.valor_rateio

    total_despesas_com_filtro = rateio_despesa_material_eletrico_role_cultural.valor_rateio + \
                                rateio_despesa_instalacao_eletrica_ptrf.valor_rateio
    results = {
        "associacao_uuid": f'{associacao.uuid}',
        "total_despesas_sem_filtro": total_despesas_sem_filtro,
        "total_despesas_com_filtro": total_despesas_com_filtro
    }

    esperado = results

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_api_get_despesas_totais_sem_passar_associacao_uuid(jwt_authenticated_client_d, associacao, despesa,
                                                            conta_associacao,
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
    response = jwt_authenticated_client_d.get(
        f'/api/rateios-despesas/totais/?aplicacao_recurso=CUSTEIO',
        content_type='application/json')
    result = json.loads(response.content)

    results = {
        'erro': 'parametros_requerido',
        'mensagem': 'É necessário enviar o uuid da conta da associação.'
    }

    esperado = results

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado


def test_api_get_despesas_totais_filtro_por_acao_associacao(jwt_authenticated_client_d, associacao, despesa,
                                                            conta_associacao,
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
    response = jwt_authenticated_client_d.get(
        f'/api/rateios-despesas/totais/?associacao__uuid={associacao.uuid}&acao_associacao__uuid={acao_associacao_ptrf.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    total_despesas_sem_filtro = rateio_despesa_material_eletrico_role_cultural.valor_rateio + \
                                rateio_despesa_instalacao_eletrica_ptrf.valor_rateio + \
                                rateio_despesa_ar_condicionado_ptrf.valor_rateio

    total_despesas_com_filtro = rateio_despesa_instalacao_eletrica_ptrf.valor_rateio + \
                                rateio_despesa_ar_condicionado_ptrf.valor_rateio
    results = {
        "associacao_uuid": f'{associacao.uuid}',
        "total_despesas_sem_filtro": total_despesas_sem_filtro,
        "total_despesas_com_filtro": total_despesas_com_filtro
    }

    esperado = results

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_api_get_despesas_totais_search_despesas_por_especificacao(jwt_authenticated_client_d, associacao, despesa,
                                                                   conta_associacao, acao,
                                                                   tipo_aplicacao_recurso_custeio,
                                                                   tipo_custeio_servico,
                                                                   especificacao_instalacao_eletrica, acao_associacao,
                                                                   especificacao_material_eletrico,
                                                                   rateio_despesa_material_eletrico_role_cultural,
                                                                   rateio_despesa_instalacao_eletrica_ptrf):
    response = jwt_authenticated_client_d.get(
        f'/api/rateios-despesas/totais/?associacao__uuid={associacao.uuid}&search=elétrico',
        content_type='application/json')
    result = json.loads(response.content)

    total_despesas_sem_filtro = rateio_despesa_material_eletrico_role_cultural.valor_rateio + \
                                rateio_despesa_instalacao_eletrica_ptrf.valor_rateio

    total_despesas_com_filtro = rateio_despesa_material_eletrico_role_cultural.valor_rateio

    results = {
        "associacao_uuid": f'{associacao.uuid}',
        "total_despesas_sem_filtro": total_despesas_sem_filtro,
        "total_despesas_com_filtro": total_despesas_com_filtro
    }

    esperado = results

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


@pytest.fixture
def despesa_11_03_2020(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='9999999',
        data_documento=date(2020, 3, 11),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=date(2020, 3, 10),
        valor_total=100.00,
    )


@pytest.fixture
def rateio_despesa_11_03_2020(associacao, despesa_11_03_2020, conta_associacao, acao,
                              tipo_aplicacao_recurso_custeio,
                              tipo_custeio_material,
                              especificacao_material_eletrico, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_11_03_2020,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=999.00,

    )


def test_api_get_despesas_totais_por_periodo(jwt_authenticated_client_d, associacao, despesa,
                                             conta_associacao, acao,
                                             tipo_aplicacao_recurso_custeio,
                                             tipo_custeio_servico,
                                             especificacao_instalacao_eletrica, acao_associacao,
                                             especificacao_material_eletrico,
                                             rateio_despesa_material_eletrico_role_cultural,
                                             rateio_despesa_instalacao_eletrica_ptrf,
                                             despesa_11_03_2020,
                                             rateio_despesa_11_03_2020
                                             ):
    response = jwt_authenticated_client_d.get(
        f'/api/rateios-despesas/totais/?associacao__uuid={associacao.uuid}&data_inicio=2020-03-11&data_fim=2020-03-11',
        content_type='application/json')
    result = json.loads(response.content)

    total_despesas_sem_filtro = rateio_despesa_material_eletrico_role_cultural.valor_rateio + \
                                rateio_despesa_instalacao_eletrica_ptrf.valor_rateio + \
                                rateio_despesa_11_03_2020.valor_rateio

    total_despesas_com_filtro = rateio_despesa_11_03_2020.valor_rateio

    results = {
        "associacao_uuid": f'{associacao.uuid}',
        "total_despesas_sem_filtro": total_despesas_sem_filtro,
        "total_despesas_com_filtro": total_despesas_com_filtro
    }

    esperado = results

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


@pytest.fixture
def despesa_fornecedor_xpto(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='9999999',
        data_documento=date(2020, 3, 11),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-00',
        nome_fornecedor='XPTO',
        tipo_transacao=tipo_transacao,
        data_transacao=date(2020, 3, 10),
        valor_total=100.00,
    )


@pytest.fixture
def rateio_despesa_fornecedor_xpto(associacao, despesa_fornecedor_xpto, conta_associacao, acao,
                                   tipo_aplicacao_recurso_custeio,
                                   tipo_custeio_material,
                                   especificacao_material_eletrico, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_fornecedor_xpto,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=777.00,

    )


def test_api_get_despesas_totais_por_fornecedor(jwt_authenticated_client_d, associacao, despesa,
                                                conta_associacao, acao,
                                                tipo_aplicacao_recurso_custeio,
                                                tipo_custeio_servico,
                                                especificacao_instalacao_eletrica, acao_associacao,
                                                especificacao_material_eletrico,
                                                rateio_despesa_material_eletrico_role_cultural,
                                                rateio_despesa_instalacao_eletrica_ptrf,
                                                despesa_fornecedor_xpto,
                                                rateio_despesa_fornecedor_xpto
                                                ):
    response = jwt_authenticated_client_d.get(
        f'/api/rateios-despesas/totais/?associacao__uuid={associacao.uuid}&fornecedor=XPTO',
        content_type='application/json')
    result = json.loads(response.content)

    total_despesas_sem_filtro = rateio_despesa_material_eletrico_role_cultural.valor_rateio + \
                                rateio_despesa_instalacao_eletrica_ptrf.valor_rateio + \
                                rateio_despesa_fornecedor_xpto.valor_rateio

    total_despesas_com_filtro = rateio_despesa_fornecedor_xpto.valor_rateio

    results = {
        "associacao_uuid": f'{associacao.uuid}',
        "total_despesas_sem_filtro": total_despesas_sem_filtro,
        "total_despesas_com_filtro": total_despesas_com_filtro
    }

    esperado = results

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
