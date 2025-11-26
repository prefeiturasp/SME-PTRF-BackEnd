import pytest
from model_bakery import baker

from ...models import OutroRecurso
from ...admin import OutroRecursoAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def outros_recursos_admin():
    return OutroRecursoAdmin(model=OutroRecurso, admin_site=site)


@pytest.fixture
def outros_recursos():
    return baker.make('OutroRecurso', nome='Outro Recurso Teste')
