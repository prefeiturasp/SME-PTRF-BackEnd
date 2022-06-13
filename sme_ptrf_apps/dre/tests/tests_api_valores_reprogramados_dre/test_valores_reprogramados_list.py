import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_valores_reprogramados_list(
    jwt_authenticated_client_dre,
    dre,
    unidade,
    unidade_valores_reprogramados,
    associacao,
    associacao_2,
    periodo_anterior,
    fechamento_conta_cheque_valores_reprogramados,
    fechamento_conta_cheque_valores_reprogramados_2,
    fechamento_conta_cartao_valores_reprogramados,
    fechamento_conta_cartao_valores_reprogramados_2,
    parametros_dre_valores_reprogramados
):
    response = jwt_authenticated_client_dre.get(
        f'/api/valores-reprogramados/?dre_uuid={dre.uuid}', content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2
