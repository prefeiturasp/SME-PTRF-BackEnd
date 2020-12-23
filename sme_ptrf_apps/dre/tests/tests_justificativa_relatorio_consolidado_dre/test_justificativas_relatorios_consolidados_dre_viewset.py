import pytest

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.justificativas_relatorios_consolidados_dre_viewset import JustificativasRelatoriosConsolidadosDreViewSet

pytestmark = pytest.mark.django_db

def test_view_set(justificativa_relatorio_dre_consolidado, usuario_permissao_ver_relatorio_consolidado):
    request = APIRequestFactory().get("")
    detalhe = JustificativasRelatoriosConsolidadosDreViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_ver_relatorio_consolidado)
    response = detalhe(request, uuid=justificativa_relatorio_dre_consolidado.uuid)

    assert response.status_code == status.HTTP_200_OK
