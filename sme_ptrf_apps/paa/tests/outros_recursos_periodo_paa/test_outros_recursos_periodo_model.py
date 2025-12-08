import pytest
from sme_ptrf_apps.paa.models import OutroRecursoPeriodoPaa
from sme_ptrf_apps.paa.fixtures.factories import OutroRecursoPeriodoFactory


@pytest.mark.django_db
def test_create_outros_recursos_periodo():
    outro_recurso_periodo = OutroRecursoPeriodoFactory()

    qs = OutroRecursoPeriodoPaa.objects.first()
    assert OutroRecursoPeriodoPaa.objects.count() == 1
    assert qs.periodo_paa == outro_recurso_periodo.periodo_paa


@pytest.mark.django_db
def test_str_representation(outros_recursos_periodo):
    assert outros_recursos_periodo is not None
    assert str(outros_recursos_periodo) == (
        f'{str(outros_recursos_periodo.outro_recurso)} - {str(outros_recursos_periodo.periodo_paa)}')
