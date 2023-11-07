import pytest
from django.contrib import admin
from ...models import SolicitacaoDeMigracao

pytestmark = pytest.mark.django_db


def test_instance_model(solicitacao_de_migracao_eol_unidade):
    model = solicitacao_de_migracao_eol_unidade
    assert isinstance(model, SolicitacaoDeMigracao)
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.eol_unidade
    assert not model.dre
    assert not model.todas_as_unidades
    assert model.status_processamento
    assert model.log_execucao


def test_str_model(solicitacao_de_migracao_eol_unidade):
    assert f"Migração da Unidade: {solicitacao_de_migracao_eol_unidade}"


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[SolicitacaoDeMigracao]
