import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.prestacoes_contas_viewset import PrestacoesContasViewSet

pytestmark = pytest.mark.django_db


def test_view_set(prestacao_conta, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = PrestacoesContasViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=prestacao_conta.uuid)

    assert response.status_code == status.HTTP_200_OK
