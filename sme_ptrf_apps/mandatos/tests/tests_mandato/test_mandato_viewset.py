import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.mandatos_viewset import MandatosViewSet

pytestmark = pytest.mark.django_db


def test_view_set(mandato_2023_a_2025, usuario_permissao_sme):
    request = APIRequestFactory().get('')
    detalhe = MandatosViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_sme)
    response = detalhe(request, uuid=mandato_2023_a_2025.uuid)
    assert response.status_code == status.HTTP_200_OK
