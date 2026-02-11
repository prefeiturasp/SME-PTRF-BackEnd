import pytest
from sme_ptrf_apps.paa.models import ModeloCargaPaa
from sme_ptrf_apps.paa.enums import TipoCargaPaaEnum

from sme_ptrf_apps.paa.fixtures.factories import ModeloCargaPaaFactory


@pytest.mark.django_db
def test_create_modelo_carga_paa():
    modelo = ModeloCargaPaaFactory()

    qs = ModeloCargaPaa.objects.get(id=modelo.id)
    assert qs is not None
    assert qs.tipo_carga == modelo.tipo_carga


@pytest.mark.django_db
def test_str_representation(modelo_carga_paa_plano_anual):
    assert str(modelo_carga_paa_plano_anual) == TipoCargaPaaEnum[modelo_carga_paa_plano_anual.tipo_carga].value
