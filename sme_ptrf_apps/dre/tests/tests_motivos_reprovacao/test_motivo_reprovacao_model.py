import pytest
from ...models import MotivoReprovacao
from django.contrib import admin

pytestmark = pytest.mark.django_db


def test_instance_model(motivo_reprovacao_x):
    model = motivo_reprovacao_x
    assert isinstance(model, MotivoReprovacao)
    assert model.id
    assert model.uuid
    assert model.motivo


def test_str_model(motivo_reprovacao_x):
    assert motivo_reprovacao_x.__str__() == 'X'


def test_meta_model(motivo_reprovacao_x):
    assert motivo_reprovacao_x._meta.verbose_name == 'Motivo de reprovação'
    assert motivo_reprovacao_x._meta.verbose_name_plural == 'Motivos de reprovação'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[MotivoReprovacao]
