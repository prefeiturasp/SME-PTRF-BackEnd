import pytest

from ...api.serializers.conta_associacao_serializer import (ContaAssociacaoSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(conta_associacao):

    serializer = ContaAssociacaoSerializer(conta_associacao)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['tipo_conta']
    assert serializer.data['associacao']
    assert serializer.data['status']
