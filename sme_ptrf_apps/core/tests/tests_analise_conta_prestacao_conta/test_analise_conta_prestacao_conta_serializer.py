import pytest

from ...api.serializers import AnaliseContaPrestacaoContaRetrieveSerializer

pytestmark = pytest.mark.django_db


def test_cobranca_prestacao_conta_list_serializer(analise_conta_prestacao_conta_2020_1):
    serializer = AnaliseContaPrestacaoContaRetrieveSerializer(analise_conta_prestacao_conta_2020_1)
    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['prestacao_conta']
    assert serializer.data['conta_associacao']
    assert serializer.data['data_extrato']
    assert serializer.data['saldo_extrato']
