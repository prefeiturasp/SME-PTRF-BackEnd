import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_reabrir_consolidado(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    consolidado_dre_teste_api_consolidado_dre,
):
    consolidado_dre_uuid = consolidado_dre_teste_api_consolidado_dre.uuid

    response = jwt_authenticated_client_dre.delete(
        f'/api/consolidados-dre/reabrir-consolidado/?uuid={consolidado_dre_uuid}',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
