import pytest
from ...models import ReceitaPrevistaPaa
from ...admin import ReceitaPrevistaPaaAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def receitas_previstas_paa_admin():
    return ReceitaPrevistaPaaAdmin(model=ReceitaPrevistaPaa, admin_site=site)
