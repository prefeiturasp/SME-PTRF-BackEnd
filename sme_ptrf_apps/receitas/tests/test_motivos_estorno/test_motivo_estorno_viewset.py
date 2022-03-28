import pytest

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.motivos_estorno_viewset import MotivosEstornoViewSet

pytestmark = pytest.mark.django_db


def test_view_set(motivo_estorno_01, usuario_permissao):
    request = APIRequestFactory().get("")
    detalhe = MotivosEstornoViewSet.as_view({"get": "retrieve"})
    force_authenticate(request, user=usuario_permissao)
    response = detalhe(request, uuid=motivo_estorno_01.uuid)

    assert response.status_code == status.HTTP_200_OK
