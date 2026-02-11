import pytest
from sme_ptrf_apps.paa.models import DocumentoPaa
from sme_ptrf_apps.paa.fixtures.factories import DocumentoPaaFactory


@pytest.mark.django_db
def test_create_documento_paa():
    recurso = DocumentoPaaFactory()

    qs = DocumentoPaa.objects.get(id=recurso.id)
    assert qs is not None


@pytest.mark.django_db
def test_str_representation(documento_paa):
    assert f'Documento PAA {DocumentoPaa.VersaoChoices(documento_paa.versao).label} gerado dia' in str(documento_paa)
