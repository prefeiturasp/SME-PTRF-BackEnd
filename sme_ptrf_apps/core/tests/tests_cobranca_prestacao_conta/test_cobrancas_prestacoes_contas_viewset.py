import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.cobrancas_prestacoes_contas_viewset import CobrancasPrestacoesContasViewSet

pytestmark = pytest.mark.django_db


def test_view_set(cobranca_prestacao_devolucao, fake_user):
    request = APIRequestFactory().get("")
    detalhe = CobrancasPrestacoesContasViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = detalhe(request, uuid=cobranca_prestacao_devolucao.uuid)

    assert response.status_code == status.HTTP_200_OK
