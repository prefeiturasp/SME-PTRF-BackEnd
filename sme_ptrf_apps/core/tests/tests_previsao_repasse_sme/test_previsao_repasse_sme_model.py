import pytest
from django.contrib import admin

from ...models import PrevisaoRepasseSme, Associacao, Periodo, ContaAssociacao

pytestmark = pytest.mark.django_db


def test_instance_model(previsao_repasse_sme):
    model = previsao_repasse_sme
    assert isinstance(model, PrevisaoRepasseSme)
    assert isinstance(model.associacao, Associacao)
    assert isinstance(model.periodo, Periodo)
    assert isinstance(model.conta_associacao, ContaAssociacao)
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.valor_capital
    assert model.valor_custeio
    assert model.valor_livre

def test_srt_model(previsao_repasse_sme):
    assert previsao_repasse_sme.__str__() == '2019.2 - Escola Teste'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[PrevisaoRepasseSme]
