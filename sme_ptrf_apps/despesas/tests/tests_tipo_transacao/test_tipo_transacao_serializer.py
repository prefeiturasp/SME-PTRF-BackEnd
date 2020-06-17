import pytest

from ...api.serializers.tipo_transacao_serializer import (TipoTransacaoSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(tipo_transacao):

    serializer = TipoTransacaoSerializer(tipo_transacao)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']
    assert serializer.data['tem_documento'] is not None
