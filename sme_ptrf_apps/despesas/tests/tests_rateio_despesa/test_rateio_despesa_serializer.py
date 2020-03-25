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

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['despesa']
    assert serializer.data['numero_documento']
    assert serializer.data['status_despesa']
    assert serializer.data['especificacao_material_servico']
    assert serializer.data['data_documento']
    assert serializer.data['aplicacao_recurso']
    assert serializer.data['acao_associacao']
    assert serializer.data['valor_total']
