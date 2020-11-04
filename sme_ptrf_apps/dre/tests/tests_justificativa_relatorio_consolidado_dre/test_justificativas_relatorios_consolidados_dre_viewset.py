import pytest

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.justificativas_relatorios_consolidados_dre_viewset import JustificativasRelatoriosConsolidadosDreViewSet

pytestmark = pytest.mark.django_db

def test_view_set(justificativa_relatorio_dre_consolidado, fake_user):
    request = APIRequestFactory().get("")
    detalhe = JustificativasRelatoriosConsolidadosDreViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = detalhe(request, uuid=justificativa_relatorio_dre_consolidado.uuid)

    assert response.status_code == status.HTTP_200_OK
