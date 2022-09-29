import pytest

from ...api.serializers import (
    AnaliseLancamentoPrestacaoContaRetrieveSerializer,
    AnaliseLancamentoPrestacaoContaUpdateSerializer
)

pytestmark = pytest.mark.django_db


def test_retrieve_serializer(analise_lancamento_receita_prestacao_conta_2020_1):
    serializer = AnaliseLancamentoPrestacaoContaRetrieveSerializer(analise_lancamento_receita_prestacao_conta_2020_1)
    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['id']
    assert serializer.data['analise_prestacao_conta']
    assert serializer.data['tipo_lancamento']
    assert serializer.data['despesa'] is None
    assert serializer.data['receita']
    assert serializer.data['resultado']
    assert serializer.data['solicitacoes_de_ajuste_da_analise'] == []
    assert serializer.data['justificativa'] is None
    assert serializer.data['status_realizacao']
    assert not serializer.data['devolucao_tesouro_atualizada']


def test_update_serializer(analise_lancamento_receita_prestacao_conta_2020_1_com_justificativa):
    serializer = AnaliseLancamentoPrestacaoContaUpdateSerializer(
        analise_lancamento_receita_prestacao_conta_2020_1_com_justificativa)
    assert serializer.data is not None
    assert serializer.data['justificativa']
