import pytest


from django.contrib import admin
from model_bakery import baker
from ...models import TipoAcertoLancamento

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_acerto_lancamento():
    return baker.make('TipoAcertoLancamento', nome='Teste', categoria='BASICO')


def test_instance_model(tipo_acerto_lancamento):
    model = tipo_acerto_lancamento
    assert isinstance(model, TipoAcertoLancamento)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.categoria


def test_srt_model(tipo_acerto_lancamento):
    assert str(tipo_acerto_lancamento) == 'Teste'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[TipoAcertoLancamento]
