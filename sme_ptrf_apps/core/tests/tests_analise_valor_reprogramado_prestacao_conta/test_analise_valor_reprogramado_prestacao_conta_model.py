import pytest
from model_bakery import baker
from django.contrib import admin
from ...models import AnaliseValorReprogramadoPrestacaoConta, PrestacaoConta, AnalisePrestacaoConta, ContaAssociacao, AcaoAssociacao

pytestmark = pytest.mark.django_db


def test_instance_model(analise_valor_reprogramado_por_acao):
    model = analise_valor_reprogramado_por_acao
    assert isinstance(model, AnaliseValorReprogramadoPrestacaoConta)
    assert isinstance(model.analise_prestacao_conta, AnalisePrestacaoConta)
    assert isinstance(model.conta_associacao, ContaAssociacao)
    assert isinstance(model.acao_associacao, AcaoAssociacao)
    assert model.analise_prestacao_conta
    assert model.conta_associacao
    assert model.acao_associacao
    assert not model.valor_saldo_reprogramado_correto
    assert model.novo_saldo_reprogramado_custeio
    assert model.novo_saldo_reprogramado_capital
    assert model.novo_saldo_reprogramado_livre


def test_srt_model(analise_valor_reprogramado_por_acao, conta_associacao, acao_associacao):
    assert f"Análise de valores reprogramados Conta {conta_associacao} - Ação {acao_associacao}"


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[AnaliseValorReprogramadoPrestacaoConta]
