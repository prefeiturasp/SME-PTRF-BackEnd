import pytest

from ...api.serializers.prestacao_conta_reprovada_nao_apresentacao_serializer import PrestacaoContaReprovadaNaoApresentacaoSerializer

pytestmark = pytest.mark.django_db


def test_serializer(prestacao_conta_reprovada_nao_apresentacao_factory):
    model = prestacao_conta_reprovada_nao_apresentacao_factory.create()
    serializer = PrestacaoContaReprovadaNaoApresentacaoSerializer(model)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['uuid']
    assert serializer.data['periodo']
    assert serializer.data['associacao']
    assert serializer.data['data_de_reprovacao']
    assert serializer.data['unidade_eol']
