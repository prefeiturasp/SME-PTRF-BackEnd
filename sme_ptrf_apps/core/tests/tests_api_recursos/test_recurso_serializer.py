import pytest

from ...api.serializers.recurso_serializer import (RecursoSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(recurso):

    serializer = RecursoSerializer(recurso)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['uuid']
    assert serializer.data['nome']
    assert serializer.data['nome_exibicao']
    assert serializer.data['criado_em']
    assert serializer.data['alterado_em']
    assert serializer.data['ativo']
    assert not serializer.data['logo']
    assert not serializer.data['icone']
    assert serializer.data['cor']
    assert not serializer.data['legado']
