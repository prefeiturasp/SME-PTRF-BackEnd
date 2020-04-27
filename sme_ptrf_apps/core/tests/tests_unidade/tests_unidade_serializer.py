import pytest

from ...api.serializers.unidade_serializer import UnidadeLookUpSerializer, UnidadeSerializer

pytestmark = pytest.mark.django_db


def test_unidade_lookup_serializer(unidade):
    unidade_serializer = UnidadeLookUpSerializer(unidade)

    assert unidade_serializer.data is not None
    assert 'id' not in unidade_serializer.data
    assert 'sigla' in unidade_serializer.data


def test_unidade_serializer(unidade):
    unidade_serializer = UnidadeSerializer(unidade)

    assert unidade_serializer.data is not None
    assert 'id' not in unidade_serializer.data
    assert unidade_serializer.data['dre']
    assert 'sigla' in unidade_serializer.data
