import pytest
import json
from rest_framework import status
from freezegun import freeze_time

pytestmark = pytest.mark.django_db


@freeze_time('2023-08-08 13:59:00')
def test_action_mandatos_anteriores(
    mandato_01_2021_a_2022_api,
    mandato_02_2023_a_2025_api,
    jwt_authenticated_client_sme,
):
    response = jwt_authenticated_client_sme.get(
        f'/api/mandatos/mandatos-anteriores/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


@freeze_time('2023-08-08 13:59:00')
def test_action_mandatos_anteriores_quantidade(
    mandato_01_2021_a_2022_api,
    mandato_02_2023_a_2025_api,
    jwt_authenticated_client_sme,
):
    response = jwt_authenticated_client_sme.get(
        f'/api/mandatos/mandatos-anteriores/',
        content_type='application/json'
    )

    result = json.loads(response.content)

    # Só deve trazer um mandato anterior, excluindo o atual
    assert len(result) == 1

    assert response.status_code == status.HTTP_200_OK




