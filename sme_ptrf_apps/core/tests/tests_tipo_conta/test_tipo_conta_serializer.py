import pytest

from ...api.serializers.tipo_conta_serializer import (TipoContaSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(tipo_conta):

    serializer = TipoContaSerializer(tipo_conta)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']
