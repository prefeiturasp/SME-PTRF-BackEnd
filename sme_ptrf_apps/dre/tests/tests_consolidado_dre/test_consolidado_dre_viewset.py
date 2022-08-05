import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.consolidados_dre_viewset import ConsolidadosDreViewSet

pytestmark = pytest.mark.django_db


def test_view_set(consolidado_dre_teste_model_consolidado_dre, usuario_permissao_atribuicao):
    request = APIRequestFactory().get('')
    detalhe = ConsolidadosDreViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_atribuicao)
    response = detalhe(request, uuid=consolidado_dre_teste_model_consolidado_dre.uuid)

    assert response.status_code == status.HTTP_200_OK

