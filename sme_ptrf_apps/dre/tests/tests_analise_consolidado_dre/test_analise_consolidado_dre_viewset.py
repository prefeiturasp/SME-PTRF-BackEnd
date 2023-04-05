import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.analises_consolidado_dre_viewset import AnalisesConsolidadoDreViewSet


pytestmark = pytest.mark.django_db


def test_view_set(analise_consolidado_dre_01, usuario_permissao_atribuicao):
    request = APIRequestFactory().get('')
    detalhe = AnalisesConsolidadoDreViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_atribuicao)
    response = detalhe(request, uuid=analise_consolidado_dre_01.uuid)

    assert response.status_code == status.HTTP_200_OK

