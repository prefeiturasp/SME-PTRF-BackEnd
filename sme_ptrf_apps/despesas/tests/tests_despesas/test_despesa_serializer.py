import pytest

from ...api.serializers.despesa_serializer import (DespesaSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(despesa):

    serializer = DespesaSerializer(despesa)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['associacao']
    assert serializer.data['numero_documento']
    assert serializer.data['data_documento']
    assert serializer.data['tipo_documento']
    assert serializer.data['cpf_cnpj_fornecedor']
    assert serializer.data['nome_fornecedor']
    assert serializer.data['tipo_transacao']
    assert serializer.data['data_transacao']
    assert serializer.data['valor_total']
    assert serializer.data['valor_recursos_proprios']
