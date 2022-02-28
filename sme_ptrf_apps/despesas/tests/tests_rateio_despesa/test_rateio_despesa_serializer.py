import pytest

from ...api.serializers.rateio_despesa_serializer import (RateioDespesaSerializer, RateioDespesaListaSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(rateio_despesa_capital):
    serializer = RateioDespesaSerializer(rateio_despesa_capital)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['despesa']
    assert serializer.data['associacao']
    assert serializer.data['conta_associacao']
    assert serializer.data['acao_associacao']
    assert serializer.data['aplicacao_recurso']
    assert serializer.data['tipo_custeio']
    assert serializer.data['especificacao_material_servico']
    assert serializer.data['valor_rateio']
    assert serializer.data['quantidade_itens_capital']
    assert serializer.data['valor_item_capital']
    assert serializer.data['numero_processo_incorporacao_capital']


def test_serializer_lista(rateio_despesa_capital):
    serializer = RateioDespesaListaSerializer(rateio_despesa_capital)

    expected_fields = (
        'uuid',
        'despesa',
        'numero_documento',
        'status_despesa',
        'especificacao_material_servico',
        'data_documento',
        'aplicacao_recurso',
        'acao_associacao',
        'valor_total',
        'conferido',
        'cpf_cnpj_fornecedor',
        'nome_fornecedor',
        'tipo_documento_nome',
        'tipo_transacao_nome',
        'data_transacao',
        'notificar_dias_nao_conferido',
    )
    assert serializer.data is not None
    for field in expected_fields:
        assert serializer.data[field] is not None

    assert serializer.data['estorno'] is None

