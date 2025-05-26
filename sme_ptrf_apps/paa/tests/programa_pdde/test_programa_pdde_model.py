import pytest
from sme_ptrf_apps.paa.models import ProgramaPdde
from sme_ptrf_apps.paa.fixtures.factories import ProgramaPddeFactory


@pytest.mark.django_db
def test_cricao_acao_pdde():
    categoria = ProgramaPddeFactory(nome="Novo Programa")

    assert ProgramaPdde.objects.count() == 1
    assert categoria.nome == "Novo Programa"


@pytest.mark.django_db
def test_str_da_model(programa_pdde):
    assert str(programa_pdde) == "Programa PDDE Teste"


@pytest.mark.django_db
def testa_duplicidade_de_cadastro(programa_pdde):
    with pytest.raises(Exception):
        ProgramaPddeFactory(nome="Programa PDDE Teste")

    with pytest.raises(Exception):
        ProgramaPddeFactory(nome="programa pdde teste")
