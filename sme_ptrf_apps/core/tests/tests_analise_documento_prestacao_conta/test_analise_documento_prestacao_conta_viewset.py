import pytest

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from ...api.views.analise_documento_prestacao_conta_viewset import AnaliseDocumentoPrestacaoContaViewSet

pytestmark = pytest.mark.django_db


def test_view_set(analise_documento_prestacao_conta_2020_1_ata_correta, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = AnaliseDocumentoPrestacaoContaViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=analise_documento_prestacao_conta_2020_1_ata_correta.uuid)

    assert response.status_code == status.HTTP_200_OK
