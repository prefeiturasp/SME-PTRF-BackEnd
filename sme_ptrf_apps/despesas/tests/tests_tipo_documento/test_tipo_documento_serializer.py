import pytest

from ...api.serializers.tipo_documento_serializer import (TipoDocumentoSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(tipo_documento):

    serializer = TipoDocumentoSerializer(tipo_documento)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']
