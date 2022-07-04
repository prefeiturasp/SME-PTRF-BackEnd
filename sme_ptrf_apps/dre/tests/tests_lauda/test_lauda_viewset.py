import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.consolidados_dre_viewset import ConsolidadosDreViewSet
from ...api.views.laudas_viewset import LaudaViewSet

pytestmark = pytest.mark.django_db


def test_view_set(lauda_teste_model_lauda, usuario_permissao_atribuicao):
    request = APIRequestFactory().get('')
    detalhe = LaudaViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_atribuicao)
    response = detalhe(request, uuid=lauda_teste_model_lauda.uuid)

    assert response.status_code == status.HTTP_200_OK

