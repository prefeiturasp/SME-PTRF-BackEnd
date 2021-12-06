import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.membros_comissoes_viewset import MembrosComissoesViewSet

pytestmark = pytest.mark.django_db


def test_view_set(membro_comissao_exame_contas, usuario_permissao_atribuicao):
    request = APIRequestFactory().get("")
    detalhe = MembrosComissoesViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_atribuicao)
    response = detalhe(request, uuid=membro_comissao_exame_contas.uuid)

    assert response.status_code == status.HTTP_200_OK
