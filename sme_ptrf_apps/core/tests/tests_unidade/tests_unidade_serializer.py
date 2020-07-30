import pytest

from ...api.serializers.unidade_serializer import (UnidadeLookUpSerializer, UnidadeSerializer, UnidadeInfoAtaSerializer,
                                                   UnidadeListSerializer)

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


def test_unidade_info_ata_serializer(unidade):
    unidade_serializer = UnidadeInfoAtaSerializer(unidade)
    assert unidade_serializer.data is not None
    assert 'tipo_unidade' in unidade_serializer.data
    assert 'nome' in unidade_serializer.data


def test_unidade_list_serializer(unidade):
    unidade_serializer = UnidadeListSerializer(unidade)
    assert unidade_serializer.data is not None
    assert 'uuid' in unidade_serializer.data
    assert 'codigo_eol' in unidade_serializer.data
    assert 'nome_com_tipo' in unidade_serializer.data
