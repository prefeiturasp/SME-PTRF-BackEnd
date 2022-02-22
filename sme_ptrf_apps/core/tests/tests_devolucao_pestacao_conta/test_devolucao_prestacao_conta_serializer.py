import pytest

from ...api.serializers import DevolucaoPrestacaoContaRetrieveSerializer

pytestmark = pytest.mark.django_db


def test_devolucao_prestacao_conta_retrieve_serializer(devolucao_prestacao_conta_2020_1, cobranca_prestacao_devolucao):
    serializer = DevolucaoPrestacaoContaRetrieveSerializer(devolucao_prestacao_conta_2020_1)
    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['prestacao_conta']
    assert serializer.data['data']
    assert serializer.data['data_limite_ue']
    assert serializer.data['cobrancas_da_devolucao']
    assert not serializer.data['data_retorno_ue']
