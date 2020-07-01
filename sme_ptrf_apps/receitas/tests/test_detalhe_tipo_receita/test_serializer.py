import pytest

from sme_ptrf_apps.receitas.api.serializers import DetalheTipoReceitaSerializer

pytestmark = pytest.mark.django_db


def test_list_serializer(detalhe_tipo_receita):
    serializer = DetalheTipoReceitaSerializer(detalhe_tipo_receita)
    assert serializer.data

    expected_fields = (
        'id',
        'nome',
    )

    for field in expected_fields:
        assert serializer.data[field]
