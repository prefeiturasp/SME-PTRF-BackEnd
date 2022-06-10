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


def test_audit_log(tipo_acerto_lancamento):
    assert tipo_acerto_lancamento.history.count() == 1  # Um log de inclusão
    assert tipo_acerto_lancamento.history.latest().action == 0  # 0-Inclusão

    tipo_acerto_lancamento.nome = "TESTE"
    tipo_acerto_lancamento.save()
    assert tipo_acerto_lancamento.history.count() == 2  # Um log de inclusão e outro de edição
    assert tipo_acerto_lancamento.history.latest().action == 1  # 1-Edição

