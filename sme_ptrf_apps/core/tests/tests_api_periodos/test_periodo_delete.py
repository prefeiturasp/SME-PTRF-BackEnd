import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import Periodo

pytestmark = pytest.mark.django_db


def test_delete_periodo(
    jwt_authenticated_client_a,
    periodo_2021_2
):
    assert Periodo.objects.filter(uuid=periodo_2021_2.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/periodos/{periodo_2021_2.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Periodo.objects.filter(uuid=periodo_2021_2.uuid).exists()
