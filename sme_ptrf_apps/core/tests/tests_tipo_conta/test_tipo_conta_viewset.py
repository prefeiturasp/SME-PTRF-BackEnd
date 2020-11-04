import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.tipo_conta_viewset import TiposContaViewSet

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_conta():
    return baker.make('TipoConta', nome='Teste')


def test_view_set(tipo_conta, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = TiposContaViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=tipo_conta.uuid)

    assert response.status_code == status.HTTP_200_OK
