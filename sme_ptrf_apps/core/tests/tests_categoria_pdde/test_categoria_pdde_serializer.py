import pytest

from ...api.serializers import CategoriaPddeSerializer

pytestmark = pytest.mark.django_db


def test_categoria_pdde_list_serializer(categoria_pdde):
    serializer = CategoriaPddeSerializer(categoria_pdde)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'nome' in serializer.data
