import pytest
from datetime import date
from ...models import OutroRecursoPeriodoPaa
from ...admin import OutroRecursoPeriodoPaaAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def outros_recursos_periodo_admin():
    return OutroRecursoPeriodoPaaAdmin(model=OutroRecursoPeriodoPaa, admin_site=site)


@pytest.fixture
def outros_recursos_periodo(periodo_paa_factory, outro_recurso_factory, outro_recurso_periodo_factory):
    periodo_paa = periodo_paa_factory.create(
        referencia='2000.10',
        data_inicial=date(2000, 1, 1),
        data_final=date(2000, 4, 30),
    )
    outro_recurso = outro_recurso_factory.create(nome='Teste 2000')
    return outro_recurso_periodo_factory.create(
        outro_recurso=outro_recurso,
        periodo_paa=periodo_paa,
        ativo=True
    )
