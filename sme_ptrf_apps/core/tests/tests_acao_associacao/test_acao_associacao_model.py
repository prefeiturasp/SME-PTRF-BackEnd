import pytest

from django.contrib import admin

from ...models import AcaoAssociacao

pytestmark = pytest.mark.django_db


def test_instance_model(acao_associacao):
    model = acao_associacao
    assert isinstance(model, AcaoAssociacao)
    assert model.associacao
    assert model.acao
    assert model.status
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(acao_associacao):
    assert acao_associacao.__str__() == 'Escola Teste - Ação PTRF - Ativa'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[AcaoAssociacao]


def test_get_valores(acao_associacao, acao, associacao):
    assert AcaoAssociacao.get_valores().count() == 1


def test_get_valores_com_inativos(acao_associacao, acao_associacao_inativa, conta_associacao_inativa, tipo_conta, associacao):
    assert AcaoAssociacao.get_valores().count() == 1
