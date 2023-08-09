import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views import CargosComposicoesViewSet

pytestmark = pytest.mark.django_db


def test_view_set(cargo_composicao_01, usuario_permissao_sme):
    request = APIRequestFactory().get('')
    detalhe = CargosComposicoesViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_sme)
    response = detalhe(request, uuid=cargo_composicao_01.uuid)
    assert response.status_code == status.HTTP_200_OK
