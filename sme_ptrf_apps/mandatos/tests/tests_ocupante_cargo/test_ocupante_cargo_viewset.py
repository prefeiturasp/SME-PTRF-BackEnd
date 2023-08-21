import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from ...api.views import OcupantesCargosViewSet

pytestmark = pytest.mark.django_db


def test_view_set(ocupante_cargo_01, usuario_permissao_sme):
    request = APIRequestFactory().get('')
    detalhe = OcupantesCargosViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_sme)
    response = detalhe(request, uuid=ocupante_cargo_01.uuid)
    assert response.status_code == status.HTTP_200_OK
