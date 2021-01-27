import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.acao_associacao_viewset import AcaoAssociacaoViewSet

pytestmark = pytest.mark.django_db


def test_view_set(acao_associacao, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = AcaoAssociacaoViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=acao_associacao.uuid)

    assert response.status_code == status.HTTP_200_OK
