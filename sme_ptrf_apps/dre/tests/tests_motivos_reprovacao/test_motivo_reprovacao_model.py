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


def test_audit_log(motivo_reprovacao_x):
    assert motivo_reprovacao_x.history.count() == 1  # Um log de inclusão
    assert motivo_reprovacao_x.history.latest().action == 0  # 0-Inclusão

    motivo_reprovacao_x.motivo = "TESTE"
    motivo_reprovacao_x.save()
    assert motivo_reprovacao_x.history.count() == 2  # Um log de inclusão e outro de edição
    assert motivo_reprovacao_x.history.latest().action == 1  # 1-Edição

