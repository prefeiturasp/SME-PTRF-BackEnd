import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.periodos_viewset import PeriodosViewSet

pytestmark = pytest.mark.django_db


def test_view_set(periodo, fake_user):
    request = APIRequestFactory().get("")
    detalhe = PeriodosViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = detalhe(request, uuid=periodo.uuid)

    assert response.status_code == status.HTTP_200_OK
