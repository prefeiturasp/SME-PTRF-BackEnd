import pytest

from ...api.serializers import OcupanteCargoSerializer

pytestmark = pytest.mark.django_db


def test_serializer(ocupante_cargo_01):
    serializer = OcupanteCargoSerializer(ocupante_cargo_01)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['uuid']
    assert serializer.data['nome']
    assert serializer.data['codigo_identificacao']
    assert serializer.data['cargo_educacao']
    assert serializer.data['representacao']
    assert serializer.data['email']
    assert serializer.data['cpf_responsavel']
    assert serializer.data['telefone']
    assert serializer.data['cep']
    assert serializer.data['bairro']
    assert serializer.data['endereco']
