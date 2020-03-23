import pytest

from ...api.serializers.tipo_aplicacao_recurso_serializer import (TipoAplicacaoRecursoSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(tipo_aplicacao_recurso):

    serializer = TipoAplicacaoRecursoSerializer(tipo_aplicacao_recurso)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']
