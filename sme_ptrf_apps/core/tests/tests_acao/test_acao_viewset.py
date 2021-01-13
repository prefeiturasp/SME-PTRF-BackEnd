import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.acoes_viewset import AcoesViewSet

pytestmark = pytest.mark.django_db


@pytest.fixture
def acao_x():
    return baker.make('Acao', nome='X')


def test_view_set(acao_x, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = AcoesViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=acao_x.uuid)

    assert response.status_code == status.HTTP_200_OK
