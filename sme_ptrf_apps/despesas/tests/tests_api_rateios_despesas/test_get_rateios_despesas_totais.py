import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_despesas_totais_filtro_por_tipo_aplicacao(jwt_authenticated_client, associacao, despesa,
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
    response = jwt_authenticated_client.get(
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


def test_api_get_despesas_totais_sem_passar_associacao_uuid(jwt_authenticated_client, associacao, despesa,
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
    response = jwt_authenticated_client.get(
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


def test_api_get_despesas_totais_filtro_por_acao_associacao(jwt_authenticated_client, associacao, despesa,
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
    response = jwt_authenticated_client.get(
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


def test_api_get_despesas_totais_search_despesas_por_especificacao(jwt_authenticated_client, associacao, despesa,
                                                                   conta_associacao, acao,
                                                                   tipo_aplicacao_recurso_custeio,
                                                                   tipo_custeio_servico,
                                                                   especificacao_instalacao_eletrica, acao_associacao,
                                                                   especificacao_material_eletrico,
                                                                   rateio_despesa_material_eletrico_role_cultural,
                                                                   rateio_despesa_instalacao_eletrica_ptrf):
    response = jwt_authenticated_client.get(
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
