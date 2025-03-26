import pytest
from model_bakery import baker

from ...models import AcaoPdde
from ...admin import AcaoPddeAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def acao_pdde_admin():
    return AcaoPddeAdmin(model=AcaoPdde, admin_site=site)


@pytest.fixture
def categoria_pdde():
    return baker.make(
        'CategoriaPdde',
        nome='Categoria PDDE Teste',
    )


@pytest.fixture
def acao_pdde(categoria_pdde):
    return baker.make(
        'AcaoPdde',
        nome='Ação PDDE Teste',
        categoria=categoria_pdde,
    )
