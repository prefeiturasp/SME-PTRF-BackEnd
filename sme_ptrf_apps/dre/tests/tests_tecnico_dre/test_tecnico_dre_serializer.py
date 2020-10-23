import pytest

from ...api.serializers.tecnico_dre_serializer import (TecnicoDreSerializer, TecnicoDreLookUpSerializer,
                                                       TecnicoDreCreateSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(tecnico_dre):
    serializer = TecnicoDreSerializer(tecnico_dre)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['dre']
    assert serializer.data['rf']
    assert serializer.data['nome']
    assert serializer.data['email']
    assert serializer.data['telefone']


def test_lookup_serializer(tecnico_dre):
    serializer = TecnicoDreLookUpSerializer(tecnico_dre)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['rf']
    assert serializer.data['nome']
    assert serializer.data['email']
    assert serializer.data['telefone']

def test_create_serializer(tecnico_dre):
    serializer = TecnicoDreCreateSerializer(tecnico_dre)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['dre']
    assert serializer.data['rf']
    assert serializer.data['nome']
    assert serializer.data['email']
    assert serializer.data['telefone']

