import pytest

from ...api.serializers import CargoComposicaoSerializer

pytestmark = pytest.mark.django_db


def test_serializer(cargo_composicao_01):
    serializer = CargoComposicaoSerializer(cargo_composicao_01)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['uuid']
    assert serializer.data['composicao']
    assert serializer.data['ocupante_do_cargo']
    assert serializer.data['cargo_associacao']
    assert not serializer.data['substituto']
    assert not serializer.data['substituido']
