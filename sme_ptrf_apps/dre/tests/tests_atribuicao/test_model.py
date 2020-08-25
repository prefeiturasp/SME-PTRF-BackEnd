import pytest
from django.contrib import admin

from sme_ptrf_apps.core.models import Unidade, Periodo
from sme_ptrf_apps.dre.models import TecnicoDre, Atribuicao

pytestmark = pytest.mark.django_db


def test_modelo_atribuicao(atribuicao):
    model = atribuicao

    assert isinstance(model.tecnico, TecnicoDre)
    assert isinstance(model.unidade, Unidade)
    assert isinstance(model.periodo, Periodo)


def test_meta_modelo(atribuicao):
    assert atribuicao._meta.verbose_name == 'Atribuição'
    assert atribuicao._meta.verbose_name_plural == 'Atribuições'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Atribuicao]
