import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_get_consolidados_dre_por_ata_uuid(
    jwt_authenticated_client_dre,
    ata_parecer_tecnico_teste_api
):
    ata_uuid = ata_parecer_tecnico_teste_api.uuid

    response = jwt_authenticated_client_dre.get(
        f'/api/consolidados-dre/consolidado-dre-por-ata-uuid/?ata={ata_uuid}',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
