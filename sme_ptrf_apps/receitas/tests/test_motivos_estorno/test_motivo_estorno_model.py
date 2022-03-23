import pytest
from django.contrib import admin
from sme_ptrf_apps.receitas.models import MotivoEstorno

pytestmark = pytest.mark.django_db


def test_model_instance(motivo_estorno_01):
    model = motivo_estorno_01

    assert isinstance(model, MotivoEstorno)


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[MotivoEstorno]


def test_str_model(motivo_estorno_01):
    assert motivo_estorno_01.__str__() == 'Motivo de estorno 01'


def test_meta_modelo(motivo_estorno_01):
    assert motivo_estorno_01._meta.verbose_name == 'Motivo de estorno'
    assert motivo_estorno_01._meta.verbose_name_plural == 'Motivos de estorno'


