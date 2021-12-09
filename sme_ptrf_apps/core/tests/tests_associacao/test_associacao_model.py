import pytest
from django.contrib import admin

from ...models import Associacao
from ....core.models import Unidade, Periodo

pytestmark = pytest.mark.django_db


def test_instance_model(associacao):
    model = associacao
    assert isinstance(model, Associacao)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.cnpj
    assert isinstance(model.unidade, Unidade)
    assert isinstance(model.periodo_inicial, Periodo)
    assert model.ccm
    assert model.email
    assert model.processo_regularidade is not None


def test_instance_model_campos_presidente_ausente(associacao_com_presidente_ausente):
    model = associacao_com_presidente_ausente
    assert model.status_presidente == 'AUSENTE'
    assert model.cargo_substituto_presidente_ausente == 'VICE_PRESIDENTE_DIRETORIA_EXECUTIVA'


def test_srt_model(associacao):
    assert associacao.__str__() == 'Escola Teste'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Associacao]
