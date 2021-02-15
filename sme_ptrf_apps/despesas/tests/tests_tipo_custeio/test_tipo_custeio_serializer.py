import pytest

from ...api.serializers.tipo_custeio_serializer import (TipoCusteioSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(tipo_custeio):

    serializer = TipoCusteioSerializer(tipo_custeio)

    assert serializer.data is not None
    assert serializer.data['nome']
    assert serializer.data['id']
    assert serializer.data['uuid']
