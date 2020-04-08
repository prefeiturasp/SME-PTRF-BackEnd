import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_despesas_por_especificacao_encontrada(client, associacao, despesa, conta_associacao, acao,
                                                       tipo_aplicacao_recurso_custeio,
                                                       tipo_custeio_servico,
                                                       especificacao_instalacao_eletrica, acao_associacao,
                                                       especificacao_material_eletrico,
                                                       rateio_despesa_material_eletrico,
                                                       rateio_despesa_instalacao_eletrica):
    response = client.get('/api/rateios-despesas/?search=elétrico', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1
