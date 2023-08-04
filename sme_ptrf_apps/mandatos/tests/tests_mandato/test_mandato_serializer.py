import pytest

from ...api.serializers.mandato_serializer import MandatoSerializer

pytestmark = pytest.mark.django_db


def test_serializer(mandato_2023_a_2025):
    serializer = MandatoSerializer(mandato_2023_a_2025)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['referencia_mandato']
    assert serializer.data['data_inicial']
    assert serializer.data['data_final']
