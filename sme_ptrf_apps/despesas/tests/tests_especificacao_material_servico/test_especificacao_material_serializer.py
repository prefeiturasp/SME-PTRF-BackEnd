import pytest

from ...api.serializers.especificacao_material_servico_serializer import (EspecificacaoMaterialServicoSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(especificacao_material_servico):

    serializer = EspecificacaoMaterialServicoSerializer(especificacao_material_servico)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['descricao']
    assert serializer.data['aplicacao_recurso']
    assert serializer.data['tipo_custeio']
