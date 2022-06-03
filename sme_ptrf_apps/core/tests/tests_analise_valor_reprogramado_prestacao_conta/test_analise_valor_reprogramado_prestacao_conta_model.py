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


def test_audit_log(analise_valor_reprogramado_por_acao):
    assert analise_valor_reprogramado_por_acao.history.count() == 1  # Um log de inclusão
    assert analise_valor_reprogramado_por_acao.history.latest().action == 0  # 0-Inclusão

    analise_valor_reprogramado_por_acao.novo_saldo_reprogramado_custeio = 100.00
    analise_valor_reprogramado_por_acao.save()
    assert analise_valor_reprogramado_por_acao.history.count() == 2  # Um log de inclusão e outro de edição
    assert analise_valor_reprogramado_por_acao.history.latest().action == 1  # 1-Edição

