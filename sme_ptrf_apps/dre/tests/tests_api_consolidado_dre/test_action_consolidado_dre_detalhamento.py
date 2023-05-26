import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_get_consolidado_dre_detalhamento(
    jwt_authenticated_client_sme,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    consolidado_dre_teste_api_consolidado_dre,
):
    consolidado_dre_uuid = consolidado_dre_teste_api_consolidado_dre.uuid

    response = jwt_authenticated_client_sme.get(
        f'/api/consolidados-dre/detalhamento/?uuid={consolidado_dre_uuid}',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
