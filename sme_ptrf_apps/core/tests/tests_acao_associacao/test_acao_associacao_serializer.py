import pytest

from ...api.serializers.acao_associacao_serializer import (AcaoAssociacaoSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(acao_associacao):

    serializer = AcaoAssociacaoSerializer(acao_associacao)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['acao']
    assert serializer.data['associacao']
    assert serializer.data['status']
