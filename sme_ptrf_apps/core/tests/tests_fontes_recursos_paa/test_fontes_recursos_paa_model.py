import pytest
from sme_ptrf_apps.core.models import FonteRecursoPaa


@pytest.mark.django_db
def test_create_fonte_recurso_paa(fonte_recurso_paa_factory):
    fonte_recurso = fonte_recurso_paa_factory.create(nome="Fonte recurso 1")

    assert FonteRecursoPaa.objects.count() == 10
    assert fonte_recurso.nome == "Fonte recurso 1"


@pytest.mark.django_db
def test_str_representation(fonte_recurso_paa):
    assert str(fonte_recurso_paa) == "Fonte recurso"

