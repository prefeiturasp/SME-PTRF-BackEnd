import pytest

from ...api.serializers.membro_comissao_serializer import MembroComissaoListSerializer

pytestmark = pytest.mark.django_db


def test_serializer(membro_comissao_exame_contas):
    serializer = MembroComissaoListSerializer(membro_comissao_exame_contas)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['rf']
    assert serializer.data['nome']
    assert serializer.data['email']
    assert serializer.data['qtd_comissoes']
    assert serializer.data['dre']
