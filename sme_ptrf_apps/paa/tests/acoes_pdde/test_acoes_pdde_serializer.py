import pytest

from ...api.serializers import AcaoPddeSerializer

pytestmark = pytest.mark.django_db


def test_acoes_pdde_list_serializer(acao_pdde):
    serializer = AcaoPddeSerializer(acao_pdde)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'nome' in serializer.data
    assert 'programa' in serializer.data
    assert 'programa_objeto' in serializer.data
    assert 'aceita_capital' in serializer.data
    assert 'aceita_custeio' in serializer.data
    assert 'aceita_livre_aplicacao' in serializer.data
