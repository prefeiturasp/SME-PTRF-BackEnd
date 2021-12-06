import pytest

from ...api.serializers.comissao_serializer import ComissaoSerializer

pytestmark = pytest.mark.django_db


def test_serializer(comissao_exame_contas):
    serializer = ComissaoSerializer(comissao_exame_contas)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['nome']
