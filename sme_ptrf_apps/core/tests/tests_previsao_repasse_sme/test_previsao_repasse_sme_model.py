import pytest
from django.contrib import admin

from ...models import PrevisaoRepasseSme, Associacao, Periodo

pytestmark = pytest.mark.django_db


def test_instance_model(previsao_repasse_sme):
    model = previsao_repasse_sme
    assert isinstance(model, PrevisaoRepasseSme)
    assert isinstance(model.associacao, Associacao)
    assert isinstance(model.periodo, Periodo)
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.valor

def test_srt_model(previsao_repasse_sme):
    assert previsao_repasse_sme.__str__() == '2019.2 - Escola Teste - 10000.5'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[PrevisaoRepasseSme]
