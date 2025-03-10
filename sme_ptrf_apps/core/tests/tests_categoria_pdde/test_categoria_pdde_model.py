import pytest
from sme_ptrf_apps.core.models import CategoriaPdde
from sme_ptrf_apps.core.fixtures.factories import CategoriaPddeFactory


@pytest.mark.django_db
def test_cricao_acao_pdde():
    categoria = CategoriaPddeFactory(nome="Nova Categoria")

    assert CategoriaPdde.objects.count() == 1
    assert categoria.nome == "Nova Categoria"


@pytest.mark.django_db
def test_str_da_model(categoria_pdde):
    assert str(categoria_pdde) == "Categoria PDDE Teste"


@pytest.mark.django_db
def testa_duplicidade_de_cadastro(categoria_pdde):
    with pytest.raises(Exception):
        CategoriaPddeFactory(nome="Categoria PDDE Teste")

    with pytest.raises(Exception):
        CategoriaPddeFactory(nome="categoria pdde teste")
