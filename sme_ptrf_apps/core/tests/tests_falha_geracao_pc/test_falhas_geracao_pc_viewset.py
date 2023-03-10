import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from ...api.views.falhas_geracao_pc_viewset import FalhaGeracaoPcViewSet

pytestmark = pytest.mark.django_db


def test_view_set(falha_geracao_pc_teste_falha_geracao_pc_01, usuario_dre_teste_falha_geracao_pc):
    request = APIRequestFactory().get("")
    detalhe = FalhaGeracaoPcViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_dre_teste_falha_geracao_pc)
    response = detalhe(request, uuid=falha_geracao_pc_teste_falha_geracao_pc_01.uuid)

    assert response.status_code == status.HTTP_200_OK
