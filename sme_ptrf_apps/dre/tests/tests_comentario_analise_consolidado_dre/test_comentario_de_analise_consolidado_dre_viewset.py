import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.comentarios_analises_consolidado_dre_viewset import ComentariosAnalisesConsolidadosDREViewSet

pytestmark = pytest.mark.django_db


def test_view_set(comentario_analise_consolidado_dre_01, usuario_permissao_atribuicao):
    request = APIRequestFactory().get('')
    detalhe = ComentariosAnalisesConsolidadosDREViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_atribuicao)
    response = detalhe(request, uuid=comentario_analise_consolidado_dre_01.uuid)

    assert response.status_code == status.HTTP_200_OK

