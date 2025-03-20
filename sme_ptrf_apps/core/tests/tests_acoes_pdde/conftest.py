import pytest
from ...models import AcaoPdde
from ...admin import AcaoPddeAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def acao_pdde_admin():
    return AcaoPddeAdmin(model=AcaoPdde, admin_site=site)
