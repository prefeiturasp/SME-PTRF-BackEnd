import pytest

from ...api.serializers.acao_associacao_serializer import (AcaoAssociacaoSerializer, AcaoAssociacaoLookUpSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(acao_associacao):
    serializer = AcaoAssociacaoSerializer(acao_associacao)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['acao']
    assert serializer.data['associacao']
    assert serializer.data['status']


def test_lookup_serializer(acao_associacao):
    serializer = AcaoAssociacaoLookUpSerializer(acao_associacao)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['id']
    assert serializer.data['nome']
