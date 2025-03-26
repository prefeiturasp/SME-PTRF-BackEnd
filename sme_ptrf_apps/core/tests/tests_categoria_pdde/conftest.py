import pytest
from model_bakery import baker

from ...models import CategoriaPdde
from ...admin import CategoriaPddeAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def categoria_pdde_admin():
    return CategoriaPddeAdmin(model=CategoriaPdde, admin_site=site)


@pytest.fixture
def categoria_pdde():
    return baker.make(
        'CategoriaPdde',
        nome='Categoria PDDE Teste',
    )


@pytest.fixture
def categoria_pdde_2():
    return baker.make(
        'CategoriaPdde',
        nome='Categoria PDDE Teste 2',
    )

@pytest.fixture
def categoria_pdde_3():
    return baker.make(
        'CategoriaPdde',
        nome='Categoria PDDE Teste 3',
    )

@pytest.fixture
def acao_pdde(categoria_pdde):
    return baker.make(
        'AcaoPdde',
        nome='Ação PDDE Teste',
        categoria=categoria_pdde,
    )

@pytest.fixture
def acao_pdde_2(categoria_pdde_2):
    return baker.make(
        'AcaoPdde',
        nome='Ação PDDE Teste 2',
        categoria=categoria_pdde_2,
    )


@pytest.fixture
def acao_pdde_3(categoria_pdde_2):
    return baker.make(
        'AcaoPdde',
        nome='Ação PDDE Teste 3',
        categoria=categoria_pdde_2,
    )
