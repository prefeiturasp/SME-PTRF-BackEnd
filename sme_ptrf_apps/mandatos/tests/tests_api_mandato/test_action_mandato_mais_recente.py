import pytest
import json
from rest_framework import status
from waffle.testutils import override_flag

pytestmark = pytest.mark.django_db


@override_flag('historico-de-membros', active=True)
def test_action_mandato_mais_recente(
    mandato_01_2021_a_2022_api,
    mandato_02_2023_a_2025_api,
    jwt_authenticated_client_sme,
):

    response = jwt_authenticated_client_sme.get(
        f'/api/mandatos/mandato-mais-recente/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


@override_flag('historico-de-membros', active=True)
def test_action_mandato_mais_recente_sem_mandatos_existentes(
    jwt_authenticated_client_sme,
):

    response = jwt_authenticated_client_sme.get(
        f'/api/mandatos/mandato-mais-recente/',
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert result == []

    assert response.status_code == status.HTTP_200_OK


