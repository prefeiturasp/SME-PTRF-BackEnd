import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.tipos_acerto_lancamento_viewset import TiposAcertoLancamentoViewSet

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_acerto_lancamento():
    return baker.make('TipoAcertoLancamento', nome='Teste', categoria='DEVOLUCAO')


def test_view_set(tipo_acerto_lancamento, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = TiposAcertoLancamentoViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=tipo_acerto_lancamento.uuid)

    assert response.status_code == status.HTTP_200_OK
