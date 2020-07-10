import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_search_despesas_por_especificacao(jwt_authenticated_client, associacao, despesa, conta_associacao,
                                                   acao,
                                                   tipo_aplicacao_recurso_custeio,
                                                   tipo_custeio_servico,
                                                   especificacao_instalacao_eletrica, acao_associacao,
                                                   especificacao_material_eletrico,
                                                   rateio_despesa_material_eletrico_role_cultural,
                                                   rateio_despesa_instalacao_eletrica_ptrf):
    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&search=elétrico',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_api_get_search_despesas_por_especificacao_ignora_acentos(jwt_authenticated_client, associacao, despesa,
                                                                  conta_associacao, acao,
                                                                  tipo_aplicacao_recurso_custeio,
                                                                  tipo_custeio_servico,
                                                                  especificacao_instalacao_eletrica, acao_associacao,
                                                                  especificacao_material_eletrico,
                                                                  rateio_despesa_material_eletrico_role_cultural,
                                                                  rateio_despesa_instalacao_eletrica_ptrf):
    response = jwt_authenticated_client.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&search=eletrico',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1, 'Deveria ter sido encontrado mesmo sem acento em elétrico.'
