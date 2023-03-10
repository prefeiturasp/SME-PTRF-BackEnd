import pytest
from rest_framework import status
pytestmark = pytest.mark.django_db


def test_action_contas_com_acertos_em_lancamentos(
    jwt_authenticated_client_a,
    associacao_teste_api_falha_geracao_pc,
    periodo_teste_api_falha_geracao_pc,
):
    associacao_uuid = associacao_teste_api_falha_geracao_pc.uuid
    periodo_uuid = periodo_teste_api_falha_geracao_pc.uuid

    response = jwt_authenticated_client_a.get(
        f'/api/falhas-geracao-pc/info-registro-falha-geracao-pc/?associacao={associacao_uuid}&periodo={periodo_uuid}',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
