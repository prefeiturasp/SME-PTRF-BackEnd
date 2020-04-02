import pytest

from sme_ptrf_apps.receitas.api.serializers import ReceitaCreateSerializer

pytestmark = pytest.mark.django_db


def test_create_serializer(receita):
    serializer = ReceitaCreateSerializer(receita)
    assert serializer.data
