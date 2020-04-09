import pytest

from ...api.serializers.associacao_serializer import (AssociacaoSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(associacao):

    serializer = AssociacaoSerializer(associacao)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']
