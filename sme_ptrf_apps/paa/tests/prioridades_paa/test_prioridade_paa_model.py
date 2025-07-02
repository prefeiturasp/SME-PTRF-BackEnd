import pytest
from sme_ptrf_apps.paa.models import PrioridadePaa
from sme_ptrf_apps.paa.fixtures.factories import PrioridadePaaFactory


@pytest.mark.django_db
def test_criacao_prioridade_paa(flag_paa, paa):
    PrioridadePaaFactory(paa=paa)
    assert PrioridadePaa.objects.count() == 1
