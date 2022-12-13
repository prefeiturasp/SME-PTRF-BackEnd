import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.analises_documentos_consolidado_dre_viewset import AnalisesDocumentosConsolidadoDreViewSet

pytestmark = pytest.mark.django_db


def test_view_set(analise_documento_consolidado_dre_01, usuario_permissao_atribuicao):
    request = APIRequestFactory().get('')
    detalhe = AnalisesDocumentosConsolidadoDreViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_atribuicao)
    response = detalhe(request, uuid=analise_documento_consolidado_dre_01.uuid)

    assert response.status_code == status.HTTP_200_OK

