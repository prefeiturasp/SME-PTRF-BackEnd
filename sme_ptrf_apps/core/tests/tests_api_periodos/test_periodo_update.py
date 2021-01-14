import json
import pytest

from datetime import date
from rest_framework import status

from sme_ptrf_apps.core.models import Periodo

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_update_periodo(periodo_2021_2):
    payload = {
        'data_prevista_repasse': '2021-07-01',
    }
    return payload


def test_update_periodo(
    jwt_authenticated_client_a,
    periodo_2021_2,
    payload_update_periodo
):

    assert Periodo.objects.get(uuid=periodo_2021_2.uuid).data_prevista_repasse != date(2021, 7, 1)

    response = jwt_authenticated_client_a.patch(
        f'/api/periodos/{periodo_2021_2.uuid}/',
        data=json.dumps(payload_update_periodo),
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert Periodo.objects.get(uuid=periodo_2021_2.uuid).data_prevista_repasse == date(2021, 7, 1)
