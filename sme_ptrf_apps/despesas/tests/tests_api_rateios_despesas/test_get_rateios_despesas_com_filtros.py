import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_despesas_filtro_por_tipo_aplicacao(client, associacao, despesa, conta_associacao, acao,
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
    response = client.get('/api/rateios-despesas/?aplicacao_recurso=CUSTEIO', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2

    response = client.get('/api/rateios-despesas/?aplicacao_recurso=CAPITAL', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_api_get_despesas_filtro_por_acao_associacao(client, associacao, despesa, conta_associacao, acao,
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
    response = client.get(f'/api/rateios-despesas/?acao_associacao={acao_associacao_ptrf.id}',
                          content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2

    response = client.get(f'/api/rateios-despesas/?acao_associacao={acao_associacao_role_cultural.id}',
                          content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1
