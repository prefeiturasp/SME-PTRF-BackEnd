import pytest
from model_bakery import baker
from rest_framework import status

from sme_ptrf_apps.core.models import ComentarioAnalisePrestacao

pytestmark = pytest.mark.django_db

@pytest.fixture
def comentario_analise_prestacao(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'ComentarioAnalisePrestacao',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        ordem=1,
        comentario='Teste',
    )


def test_delete_cobranca_prestacao_conta(jwt_authenticated_client, comentario_analise_prestacao):
    assert ComentarioAnalisePrestacao.objects.filter(uuid=comentario_analise_prestacao.uuid).exists(), "Deveria já existir"

    response = jwt_authenticated_client.delete(
        f'/api/comentarios-de-analises/{comentario_analise_prestacao.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not ComentarioAnalisePrestacao.objects.filter(uuid=comentario_analise_prestacao.uuid).exists(), "Não foi deletado"
