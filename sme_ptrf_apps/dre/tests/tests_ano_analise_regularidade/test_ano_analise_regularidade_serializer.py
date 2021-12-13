import pytest

from ...api.serializers.ano_analise_regularidade_serializer import AnoAnaliseRegularidadeListSerializer

pytestmark = pytest.mark.django_db


def test_serializer(ano_analise_regularidade_2021):
    serializer = AnoAnaliseRegularidadeListSerializer(ano_analise_regularidade_2021)

    assert serializer.data is not None
    assert serializer.data['ano']
