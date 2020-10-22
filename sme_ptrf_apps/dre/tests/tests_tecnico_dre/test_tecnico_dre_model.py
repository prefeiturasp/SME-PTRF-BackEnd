import pytest
from django.contrib import admin

from ...models import TecnicoDre
from ....core.models import Unidade

pytestmark = pytest.mark.django_db

def test_instance_model(tecnico_dre):
    model = tecnico_dre
    assert isinstance(model, TecnicoDre)
    assert isinstance(model.dre, Unidade)
    assert model.nome
    assert model.rf
    assert model.id
    assert model.uuid
    assert model.email
    assert model.telefone


def test_srt_model(tecnico_dre):
    assert tecnico_dre.__str__() == 'Nome: José Testando, RF: 271170'


def test_meta_modelo(tecnico_dre):
    assert tecnico_dre._meta.verbose_name == 'Técnico de DRE'
    assert tecnico_dre._meta.verbose_name_plural == 'Técnicos de DREs'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[TecnicoDre]
