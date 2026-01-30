import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
def test_str_representation(paa):
    assert str(paa) == f"{paa.periodo_paa.referencia} - {paa.associacao}"


@pytest.mark.django_db
def test_paa_model_tem_campos_acoes_conclusao(paa_factory, periodo_paa_1):
    """Testa que o modelo PAA tem os campos ManyToMany para ações na conclusão"""
    paa = paa_factory.create(periodo_paa=periodo_paa_1)
    assert hasattr(paa, 'acoes_conclusao')
    assert hasattr(paa, 'acoes_pdde_conclusao')
    assert hasattr(paa, 'outros_recursos_periodo_conclusao')
    assert paa.acoes_conclusao.count() == 0
    assert paa.acoes_pdde_conclusao.count() == 0
    assert paa.outros_recursos_periodo_conclusao.count() == 0
