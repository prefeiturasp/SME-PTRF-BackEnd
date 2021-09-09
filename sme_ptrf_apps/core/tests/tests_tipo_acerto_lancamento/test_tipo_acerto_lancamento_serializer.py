import pytest
from model_bakery import baker

from ...api.serializers.tipo_acerto_lancamento_serializer import (TipoAcertoLancamentoSerializer)

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_acerto_lancamento():
    return baker.make('TipoAcertoLancamento', nome='Teste', categoria='BASICO')


def test_serializer(tipo_acerto_lancamento):

    serializer = TipoAcertoLancamentoSerializer(tipo_acerto_lancamento)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']
    assert serializer.data['categoria']
    assert serializer.data['uuid']
