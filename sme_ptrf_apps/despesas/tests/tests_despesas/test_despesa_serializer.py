import pytest

from ...api.serializers.despesa_serializer import (DespesaSerializer, DespesaCreateSerializer, DespesaListSerializer)

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
    assert serializer.data['documento_transacao'] is not None
    assert serializer.data['data_transacao']
    assert serializer.data['valor_total']
    assert serializer.data['valor_recursos_proprios']


def test_create_serializer(despesa, rateio_despesa_capital):

    serializer = DespesaCreateSerializer(despesa)

    assert serializer.data is not None


def test_list_serializer(despesa):

    serializer = DespesaListSerializer(despesa)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['associacao']
    assert serializer.data['numero_documento']
    assert serializer.data['data_documento']
    assert serializer.data['tipo_documento']
    assert serializer.data['cpf_cnpj_fornecedor']
    assert serializer.data['nome_fornecedor']
    assert serializer.data['valor_total']
    assert serializer.data['valor_ptrf']
