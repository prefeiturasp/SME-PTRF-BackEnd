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
        'tipo_receita',
        'acao_associacao',
        'conta_associacao',
        'conferido',
        'detalhe_tipo_receita',
        'notificar_dias_nao_conferido',
        'saida_do_recurso',
    )

    for field in expected_fields:
        assert serializer.data[field] is not None, f'Não encontrado o campo {field} no serializer ReceitaLista.'


def test_list_serializer_sem_detalhe_tipo_receita(receita_sem_detalhe_tipo_receita):
    serializer = ReceitaListaSerializer(receita_sem_detalhe_tipo_receita)
    assert serializer.data

    expected_fields = (
        'uuid',
        'data',
        'valor',
        'tipo_receita',
        'acao_associacao',
        'conta_associacao',
        'conferido',
        'detalhe_outros'
    )

    for field in expected_fields:
        assert serializer.data[field], f'Não encontrado o campo {field} no serializer ReceitaLista.'
