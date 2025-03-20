import pytest
from ...models import CategoriaPdde
from ...admin import CategoriaPddeAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def categoria_pdde_admin():
    return CategoriaPddeAdmin(model=CategoriaPdde, admin_site=site)
