import pytest

from sme_ptrf_apps.receitas.api.serializers import ReceitaCreateSerializer, ReceitaListaSerializer

pytestmark = pytest.mark.django_db


def test_create_serializer(receita):
    serializer = ReceitaCreateSerializer(receita)
    assert serializer.data


def test_list_serializer(receita, detalhe_tipo_receita):
    serializer = ReceitaListaSerializer(receita)
    assert serializer.data

    expected_fields = (
        'uuid',
        'data',
        'valor',
        'descricao',
        'tipo_receita',
        'acao_associacao',
        'conta_associacao',
        'conferido',
        'detalhe_tipo_receita',
        'detalhe_outros'
    )

    for field in expected_fields:
        assert serializer.data[field]
