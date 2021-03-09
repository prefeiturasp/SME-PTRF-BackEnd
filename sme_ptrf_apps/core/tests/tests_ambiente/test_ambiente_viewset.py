import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from ...api.views.ambientes_viewset import AmbientesViewSet

pytestmark = pytest.mark.django_db


def test_ambiente_viewset(ambiente_dev, usuario):
    request = APIRequestFactory().get('')
    detalhe = AmbientesViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario)
    response = detalhe(request, pk=ambiente_dev.id)

    assert response.status_code == status.HTTP_200_OK
