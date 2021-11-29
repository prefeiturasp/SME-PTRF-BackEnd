import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from ...api.views.analise_valor_reprogramado_prestacao_conta_viewset import AnaliseValorReprogramadoPrestacaoContaViewSet

pytestmark = pytest.mark.django_db


def test_analise_valor_reprogramado_prestacao_conta_viewset(analise_valor_reprogramado_por_acao, usuario_permissao_associacao):
    request = APIRequestFactory().get('')
    detalhe = AnaliseValorReprogramadoPrestacaoContaViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=analise_valor_reprogramado_por_acao.uuid)

    assert response.status_code == status.HTTP_200_OK
