import pytest
from model_bakery import baker

from ...api.serializers import TipoDocumentoPrestacaoContaSerializer
pytestmark = pytest.mark.django_db

@pytest.fixture
def tipo_documento_prestacao_conta():
    return baker.make('TipoDocumentoPrestacaoConta', nome='Cópia da ata da prestação de contas', documento_por_conta=True)


def test_serializer(tipo_documento_prestacao_conta):

    serializer = TipoDocumentoPrestacaoContaSerializer(tipo_documento_prestacao_conta)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['uuid']
    assert serializer.data['nome']
    assert serializer.data['documento_por_conta']
