import pytest

from sme_ptrf_apps.paa.api.serializers import PaaSerializer

pytestmark = pytest.mark.django_db


def test_paa_retriever_serializer(paa):
    serializer = PaaSerializer(paa)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'periodo_paa' in serializer.data
    assert 'associacao' in serializer.data
    assert 'periodo_paa_objeto' in serializer.data
    assert 'saldo_congelado_em' in serializer.data
    assert 'texto_introducao' in serializer.data
    assert 'texto_conclusao' in serializer.data
    assert 'status' in serializer.data


def test_paa_model_tem_campos_acoes_conclusao(paa):
    """Testa que o modelo PAA tem os campos ManyToMany para ações na conclusão"""
    assert hasattr(paa, 'acoes_conclusao')
    assert hasattr(paa, 'acoes_pdde_conclusao')
    assert hasattr(paa, 'outros_recursos_periodo_conclusao')
    assert paa.acoes_conclusao.count() == 0
    assert paa.acoes_pdde_conclusao.count() == 0
    assert paa.outros_recursos_periodo_conclusao.count() == 0