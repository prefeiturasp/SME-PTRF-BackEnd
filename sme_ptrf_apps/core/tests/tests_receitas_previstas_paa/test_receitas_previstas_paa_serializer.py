import pytest

from ...api.serializers import ReceitaPrevistaPaaSerializer

pytestmark = pytest.mark.django_db


def test_receita_prevista_serializer_list_serializer(receita_prevista_paa):
    serializer = ReceitaPrevistaPaaSerializer(receita_prevista_paa)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'acao_associacao' in serializer.data
    assert 'previsao_valor_custeio' in serializer.data
    assert 'previsao_valor_capital' in serializer.data
    assert 'previsao_valor_livre' in serializer.data
