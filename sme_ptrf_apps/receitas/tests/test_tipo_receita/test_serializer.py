import pytest

from sme_ptrf_apps.receitas.api.serializers import TipoReceitaSerializer, TipoReceitaEDetalhesSerializer

pytestmark = pytest.mark.django_db


def test_list_serializer(tipo_receita):
    serializer = TipoReceitaSerializer(tipo_receita)
    assert serializer.data

    expected_fields = (
        'id',
        'nome',
    )

    for field in expected_fields:
        assert serializer.data[field]


def test_detalhes_serializer(tipo_receita, detalhe_tipo_receita):
    serializer = TipoReceitaEDetalhesSerializer(tipo_receita)
    assert serializer.data

    expected_fields = (
        'id',
        'nome',
        'detalhes_tipo_receita'
    )

    for field in expected_fields:
        assert serializer.data[field]
