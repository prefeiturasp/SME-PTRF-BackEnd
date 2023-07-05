import pytest

from ...api.serializers import AnaliseContaPrestacaoContaRetrieveSerializer

pytestmark = pytest.mark.django_db


def test_cobranca_prestacao_conta_list_serializer(analise_conta_prestacao_conta_2020_1_solicitar_envio_do_comprovante_do_saldo_da_conta):
    serializer = AnaliseContaPrestacaoContaRetrieveSerializer(analise_conta_prestacao_conta_2020_1_solicitar_envio_do_comprovante_do_saldo_da_conta)
    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['prestacao_conta']
    assert serializer.data['conta_associacao']
    assert serializer.data['data_extrato']
    assert serializer.data['saldo_extrato']
    assert serializer.data['solicitar_envio_do_comprovante_do_saldo_da_conta']
    assert serializer.data['observacao_solicitar_envio_do_comprovante_do_saldo_da_conta']
