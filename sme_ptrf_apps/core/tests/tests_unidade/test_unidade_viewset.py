import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.unidades_viewset import UnidadesViewSet

pytestmark = pytest.mark.django_db


def test_view_set(unidade, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = UnidadesViewSet.as_view({'get':'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=unidade.uuid)

    assert response.status_code == status.HTTP_200_OK
