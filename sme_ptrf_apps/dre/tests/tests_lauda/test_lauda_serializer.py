import pytest

from ...api.serializers.lauda_serializer import LaudaSerializer

pytestmark = pytest.mark.django_db


def test_serializer(lauda_teste_model_lauda):
    serializer = LaudaSerializer(lauda_teste_model_lauda)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['arquivo_lauda_txt'] is None
    assert serializer.data['consolidado_dre']
    assert serializer.data['tipo_conta']
    assert serializer.data['usuario']
    assert serializer.data['status']
