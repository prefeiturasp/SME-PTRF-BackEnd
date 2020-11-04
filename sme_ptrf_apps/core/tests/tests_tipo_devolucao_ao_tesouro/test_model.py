import pytest


from django.contrib import admin
from model_bakery import baker
from ...models import TipoDevolucaoAoTesouro

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_devolucao_ao_tesouro():
    return baker.make('TipoDevolucaoAoTesouro', nome='Teste')


def test_instance_model(tipo_devolucao_ao_tesouro):
    model = tipo_devolucao_ao_tesouro
    assert isinstance(model, TipoDevolucaoAoTesouro)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(tipo_devolucao_ao_tesouro):
    assert str(tipo_devolucao_ao_tesouro) == 'Teste'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[TipoDevolucaoAoTesouro]
