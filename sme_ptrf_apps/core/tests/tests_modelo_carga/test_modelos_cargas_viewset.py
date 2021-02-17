import pytest

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.modelos_cargas_viewset import ModelosCargasViewSet

pytestmark = pytest.mark.django_db


def test_view_set(modelo_carga_associacao, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = ModelosCargasViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, tipo_carga=modelo_carga_associacao.tipo_carga)

    assert response.status_code == status.HTTP_200_OK
