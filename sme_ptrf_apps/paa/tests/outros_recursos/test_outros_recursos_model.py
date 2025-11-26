import pytest
from sme_ptrf_apps.paa.models import OutroRecurso
from sme_ptrf_apps.paa.fixtures.factories import OutroRecursoFactory


@pytest.mark.django_db
def test_create_outros_recursos():
    recurso = OutroRecursoFactory(nome="Outro Recurso Novo")

    qs = OutroRecurso.objects.first()
    assert OutroRecurso.objects.count() == 1
    assert qs.nome == recurso.nome


@pytest.mark.django_db
def test_str_representation(outros_recursos):
    assert str(outros_recursos) == "Outro Recurso Teste"
