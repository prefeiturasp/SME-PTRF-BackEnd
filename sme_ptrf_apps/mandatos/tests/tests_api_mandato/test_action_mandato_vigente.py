import pytest
from rest_framework import status
from freezegun import freeze_time

pytestmark = pytest.mark.django_db


@freeze_time('2023-08-08 13:59:00')
def test_action_mandado_vigente(
    mandato_01_2021_a_2022_api,
    mandato_02_2023_a_2025_api,
    jwt_authenticated_client_sme,
    associacao
):
    response = jwt_authenticated_client_sme.get(
        f'/api/mandatos/mandato-vigente/?associacao_uuid={associacao.uuid}',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
