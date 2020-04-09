import pytest

from ...api.serializers.fornecedor_serializer import (FornecedorSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(fornecedor_jose):
    serializer = FornecedorSerializer(fornecedor_jose)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['uuid']
    assert serializer.data['cpf_cnpj']
    assert serializer.data['nome']
