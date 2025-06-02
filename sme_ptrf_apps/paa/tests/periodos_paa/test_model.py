import pytest
from django.core.exceptions import ValidationError
from sme_ptrf_apps.paa.models import PeriodoPaa

pytestmark = pytest.mark.django_db


def test_periodo_vigente(periodo_paa_1, periodo_paa_2):
    assert PeriodoPaa.periodo_vigente() == periodo_paa_1


def test_validacao_datas():
    with pytest.raises(ValidationError) as e:
        PeriodoPaa.objects.create(
            referencia="Periodo 01/2025 a 03/2025",
            data_inicial="2025-03-01",
            data_final="2025-03-31"
        )
    assert str(e.value) == "{'__all__': ['Data final deve ser maior que a data inicial']}"


def test_validacao_data_final():
    with pytest.raises(ValidationError) as e:
        PeriodoPaa.objects.create(
            referencia="Periodo 01/2025 a 03/2025",
            data_inicial="2025-03-01",
            data_final="2025-01-31"
        )
    assert str(e.value) == "{'__all__': ['Data final deve ser maior que a data inicial']}"
