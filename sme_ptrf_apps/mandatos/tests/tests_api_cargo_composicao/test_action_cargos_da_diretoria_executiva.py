import pytest
import json
from rest_framework import status
from waffle.testutils import override_flag

pytestmark = pytest.mark.django_db


@override_flag('historico-de-membros', active=True)
def test_action_cargos_da_diretoria_executiva(
    jwt_authenticated_client_sme,
):

    response = jwt_authenticated_client_sme.get(
        f'/api/cargos-composicao/cargos-diretoria-executiva/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK



