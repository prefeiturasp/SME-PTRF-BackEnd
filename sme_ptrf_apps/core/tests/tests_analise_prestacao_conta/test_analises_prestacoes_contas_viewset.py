import pytest

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.analises_prestacoes_contas_viewset import AnalisesPrestacoesContasViewSet

pytestmark = pytest.mark.django_db


def test_view_set(analise_prestacao_conta_2020_1, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = AnalisesPrestacoesContasViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=analise_prestacao_conta_2020_1.uuid)

    assert response.status_code == status.HTTP_200_OK
