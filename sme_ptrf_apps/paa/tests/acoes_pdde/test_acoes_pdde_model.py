import pytest
from sme_ptrf_apps.paa.models import AcaoPdde
from sme_ptrf_apps.paa.fixtures.factories import AcaoPddeFactory


@pytest.mark.django_db
def test_create_acao_pdde():
    acao = AcaoPddeFactory(nome="Ação PDDE Novo")

    assert AcaoPdde.objects.count() == 1
    assert acao.nome == "Ação PDDE Novo"
    assert acao.programa is not None


@pytest.mark.django_db
def test_str_representation(acao_pdde):
    assert str(acao_pdde) == "Ação PDDE Teste"


@pytest.mark.django_db
def test_acao_pdde_programa_objeto():
    acao = AcaoPddeFactory(nome="Ação PDDE Novo")

    assert acao.programa == acao.programa_objeto()
