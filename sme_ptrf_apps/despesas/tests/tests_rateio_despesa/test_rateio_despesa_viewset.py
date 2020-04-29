import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.rateios_despesas_viewset import RateiosDespesasViewSet

pytestmark = pytest.mark.django_db


def test_view_set(rateio_despesa_capital, jwt_authenticated_client):
    response = jwt_authenticated_client.get(f'/api/rateios-despesas/{rateio_despesa_capital.uuid}/')
    assert response.status_code == status.HTTP_200_OK

