import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_get_consolidado_dre_pcs_em_retificacao(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    retificacao_dre_teste_api_consolidado_dre,
):
    retificacao_uuid = retificacao_dre_teste_api_consolidado_dre.uuid

    response = jwt_authenticated_client_dre.get(
        f'/api/consolidados-dre/{retificacao_uuid}/pcs-do-consolidado/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
