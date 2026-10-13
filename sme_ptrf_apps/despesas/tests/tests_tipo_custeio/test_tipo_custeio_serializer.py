import pytest

from ...api.serializers.tipo_custeio_serializer import (
    TipoCusteioSerializer, TipoCusteioLookUpSerializer
)

pytestmark = pytest.mark.django_db


def test_serializer(tipo_custeio):

    serializer = TipoCusteioSerializer(tipo_custeio)

    assert serializer.data is not None
    assert serializer.data['nome']
    assert serializer.data['id']
    assert serializer.data['uuid']
    assert serializer.data['eh_tributos_e_tarifas'] is not None
    assert 'unidades' in serializer.data
    assert 'uso_associacao' in serializer.data
    assert 'todas_unidades_selecionadas' in serializer.data


def test_serializer_lookup(tipo_custeio):

    serializer = TipoCusteioLookUpSerializer(tipo_custeio)

    assert serializer.data is not None
    assert 'nome' in serializer.data
    assert 'id' in serializer.data
    assert 'uuid' in serializer.data
    assert 'eh_tributos_e_tarifas' in serializer.data
    assert 'unidades' not in serializer.data
    assert 'uso_associacao' not in serializer.data
    assert 'todas_unidades_selecionadas' not in serializer.data
