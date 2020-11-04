import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.comentarios_analises_prestacoes_viewset import ComentariosAnalisesPrestacoesViewSet

pytestmark = pytest.mark.django_db

@pytest.fixture
def comentario_analise_prestacao(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'ComentarioAnalisePrestacao',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        ordem=1,
        comentario='Teste',
    )


def test_view_set(comentario_analise_prestacao, fake_user):
    request = APIRequestFactory().get("")
    detalhe = ComentariosAnalisesPrestacoesViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = detalhe(request, uuid=comentario_analise_prestacao.uuid)

    assert response.status_code == status.HTTP_200_OK
