import pytest

from ...api.serializers.modelo_carga_serializer import (ModeloCargaSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(modelo_carga_associacao):

    serializer = ModeloCargaSerializer(modelo_carga_associacao)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['id']
    assert serializer.data['tipo_carga']
    assert serializer.data['arquivo']
