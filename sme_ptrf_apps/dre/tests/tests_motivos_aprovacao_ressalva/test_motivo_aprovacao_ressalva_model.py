import pytest
from ...models import MotivoAprovacaoRessalva
from django.contrib import admin

pytestmark = pytest.mark.django_db


def test_instance_model(motivo_aprovacao_ressalva_x):
    model = motivo_aprovacao_ressalva_x
    assert isinstance(model, MotivoAprovacaoRessalva)
    assert model.id
    assert model.uuid
    assert model.motivo


def test_str_model(motivo_aprovacao_ressalva_x):
    assert motivo_aprovacao_ressalva_x.__str__() == 'X'


def test_meta_model(motivo_aprovacao_ressalva_x):
    assert motivo_aprovacao_ressalva_x._meta.verbose_name == 'Motivo de aprovação com ressalva'
    assert motivo_aprovacao_ressalva_x._meta.verbose_name_plural == 'Motivos de aprovação com ressalva'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[MotivoAprovacaoRessalva]
