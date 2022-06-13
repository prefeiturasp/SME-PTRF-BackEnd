import pytest
from rest_framework import status
import json

pytestmark = pytest.mark.django_db


def test_endpoint(
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
    response = jwt_authenticated_client_dre.get(f'/api/valores-reprogramados/?dre_uuid={dre.uuid}')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2


def test_endpoint_tabelas(jwt_authenticated_client_dre):
    response = jwt_authenticated_client_dre.get(f'/api/valores-reprogramados/tabelas/')
    assert response.status_code == status.HTTP_200_OK

