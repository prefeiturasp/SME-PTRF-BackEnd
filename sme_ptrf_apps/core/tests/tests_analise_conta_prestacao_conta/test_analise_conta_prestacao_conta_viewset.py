import pytest

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from ...api.views.analise_conta_prestacao_conta_viewset import AnaliseContaPrestacaoContaViewSet

pytestmark = pytest.mark.django_db


def test_view_set(analise_conta_prestacao_conta_2020_1_solicitar_envio_do_comprovante_do_saldo_da_conta, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = AnaliseContaPrestacaoContaViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=analise_conta_prestacao_conta_2020_1_solicitar_envio_do_comprovante_do_saldo_da_conta.uuid)

    assert response.status_code == status.HTTP_200_OK
