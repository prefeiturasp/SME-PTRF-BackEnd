import pytest
from model_bakery import baker

from ...models import AcaoPdde
from ...admin import AcaoPddeAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def acao_pdde_admin():
    return AcaoPddeAdmin(model=AcaoPdde, admin_site=site)


@pytest.fixture
def acao_pdde(programa_pdde):
    return baker.make(
        'AcaoPdde',
        nome='Ação PDDE Teste',
        programa=programa_pdde,
    )
