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


def test_audit_log(previsao_repasse_sme):
    assert previsao_repasse_sme.history.count() == 1  # Um log de inclusão
    assert previsao_repasse_sme.history.latest().action == 0  # 0-Inclusão

    previsao_repasse_sme.valor_capital = 100.00
    previsao_repasse_sme.save()
    assert previsao_repasse_sme.history.count() == 2  # Um log de inclusão e outro de edição
    assert previsao_repasse_sme.history.latest().action == 1  # 1-Edição
