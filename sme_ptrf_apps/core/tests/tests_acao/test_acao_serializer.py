import pytest

from ...api.serializers.acao_serializer import (AcaoSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(acao):

    serializer = AcaoSerializer(acao)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']
    assert not serializer.data['e_recursos_proprios']
