import pytest

from ...api.serializers.rateio_despesa_serializer import (RateioDespesaSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(rateio_despesa_capital):

    serializer = RateioDespesaSerializer(rateio_despesa_capital)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['despesa']
    assert serializer.data['associacao']
    assert serializer.data['conta_associacao']
    assert serializer.data['acao_associacao']
    assert serializer.data['tipo_aplicacao_recurso']
    assert serializer.data['tipo_custeio']
    assert serializer.data['especificacao_material_servico']
    assert serializer.data['valor_rateio']
    assert serializer.data['quantidade_itens_capital']
    assert serializer.data['valor_item_capital']
    assert serializer.data['numero_processo_incorporacao_capital']
