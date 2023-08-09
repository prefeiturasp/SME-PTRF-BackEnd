import pytest

from ...api.serializers.composicao_serializer import ComposicaoSerializer

pytestmark = pytest.mark.django_db


def test_serializer(composicao_01_2023_a_2025):
    serializer = ComposicaoSerializer(composicao_01_2023_a_2025)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['uuid']
    assert serializer.data['associacao']
    assert serializer.data['mandato']
    assert serializer.data['data_inicial']
    assert serializer.data['data_final']
