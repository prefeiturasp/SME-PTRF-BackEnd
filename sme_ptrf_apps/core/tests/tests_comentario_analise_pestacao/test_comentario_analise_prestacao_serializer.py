import pytest
from model_bakery import baker

from ...api.serializers import ComentarioAnalisePrestacaoRetrieveSerializer

pytestmark = pytest.mark.django_db

@pytest.fixture
def comentario_analise_prestacao(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'ComentarioAnalisePrestacao',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        ordem=1,
        comentario='Teste',
    )


def test_comentario_analise_prestacao_retrieve_serializer(comentario_analise_prestacao):
    serializer = ComentarioAnalisePrestacaoRetrieveSerializer(comentario_analise_prestacao)
    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['prestacao_conta']
    assert serializer.data['ordem']
    assert serializer.data['comentario']
