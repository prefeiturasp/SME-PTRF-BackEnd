import pytest


from django.contrib import admin
from model_bakery import baker
from ...models import Remetente

pytestmark = pytest.mark.django_db


@pytest.fixture
def remetente():
    return baker.make('Remetente', nome='SME')


def test_instance_model(remetente):
    model = remetente
    assert isinstance(model, Remetente)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(remetente):
    assert str(remetente) == 'SME'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Remetente]
