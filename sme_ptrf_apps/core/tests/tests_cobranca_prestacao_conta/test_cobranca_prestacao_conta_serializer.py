import pytest

from ...api.serializers import CobrancaPrestacaoContaListSerializer

pytestmark = pytest.mark.django_db


def test_cobranca_prestacao_conta_list_serializer(cobranca_prestacao_recebimento):
    serializer = CobrancaPrestacaoContaListSerializer(cobranca_prestacao_recebimento)
    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['prestacao_conta']
    assert serializer.data['data']
    assert serializer.data['tipo']
    assert serializer.data['associacao']
    assert serializer.data['periodo']
