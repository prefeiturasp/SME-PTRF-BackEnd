import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.rateios_despesas_viewset import RateiosDespesasViewSet

pytestmark = pytest.mark.django_db


def test_view_set(rateio_despesa_capital, fake_user):
    request = APIRequestFactory().get("")
    detalhe = RateiosDespesasViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = detalhe(request, uuid=rateio_despesa_capital.uuid)

    assert response.status_code == status.HTTP_200_OK
