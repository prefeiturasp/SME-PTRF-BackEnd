import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from waffle.testutils import override_flag
from ...api.views.prestacoes_contas_reprovadas_nao_apresentacao_viewset import \
    PrestacaoContaReprovadaNaoApresentacaoViewSet

pytestmark = pytest.mark.django_db


@override_flag('pc-reprovada-nao-apresentacao', active=True)
def test_view_set(prestacao_conta_reprovada_nao_apresentacao_factory, usuario_permissao_associacao):
    model = prestacao_conta_reprovada_nao_apresentacao_factory.create()
    request = APIRequestFactory().get("")
    detalhe = PrestacaoContaReprovadaNaoApresentacaoViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=model.uuid)

    assert response.status_code == status.HTTP_200_OK
