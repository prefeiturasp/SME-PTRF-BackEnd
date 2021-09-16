import pytest
from model_bakery import baker

from ...api.serializers.tipo_acerto_documento_serializer import (TipoAcertoDocumentoSerializer)

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_documento_prestacao_conta_ata():
    return baker.make('TipoDocumentoPrestacaoConta', nome='Cópia da ata da prestação de contas')


@pytest.fixture
def tipo_acerto_documento_assinatura(tipo_documento_prestacao_conta_ata):
    tipo_acerto = baker.make('TipoAcertoDocumento', nome='Enviar com assinatura')
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_ata)
    tipo_acerto.save()
    return tipo_acerto


def test_serializer(tipo_acerto_documento_assinatura):

    serializer = TipoAcertoDocumentoSerializer(tipo_acerto_documento_assinatura)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']
    assert serializer.data['uuid']
