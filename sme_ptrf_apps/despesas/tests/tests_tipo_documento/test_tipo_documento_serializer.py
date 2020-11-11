import pytest

from ...api.serializers.tipo_documento_serializer import (TipoDocumentoSerializer, TipoDocumentoListSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(tipo_documento):

    serializer = TipoDocumentoSerializer(tipo_documento)
    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']
    assert serializer.data['apenas_digitos'] is not None
    assert serializer.data['numero_documento_digitado'] is not None


def test_Listserializer(tipo_documento):

    serializer = TipoDocumentoSerializer(tipo_documento)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']
