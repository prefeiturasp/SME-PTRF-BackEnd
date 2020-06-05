import pytest
from django.contrib import admin

from ...models import FechamentoPeriodo, Associacao, Periodo, ContaAssociacao, AcaoAssociacao, STATUS_FECHADO

pytestmark = pytest.mark.django_db


def test_instance_model(fechamento_periodo):
    model = fechamento_periodo
    assert isinstance(model, FechamentoPeriodo)
    assert isinstance(model.associacao, Associacao)
    assert isinstance(model.periodo, Periodo)
    assert isinstance(model.conta_associacao, ContaAssociacao)
    assert isinstance(model.acao_associacao, AcaoAssociacao)
    assert isinstance(model.fechamento_anterior, FechamentoPeriodo)
    assert model.total_receitas_capital
    assert model.total_receitas_custeio
    assert model.total_repasses_capital
    assert model.total_repasses_custeio
    assert model.total_despesas_capital
    assert model.total_repasses_custeio
    assert model.saldo_reprogramado_capital
    assert model.saldo_reprogramado_custeio
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.status == STATUS_FECHADO
    assert model.total_receitas_nao_conciliadas_capital
    assert model.total_receitas_nao_conciliadas_custeio
    assert model.total_despesas_nao_conciliadas_capital
    assert model.total_despesas_nao_conciliadas_custeio
    assert model.especificacoes_despesas


def test_srt_model(fechamento_periodo):
    assert fechamento_periodo.__str__() == '2019.2 - 2019-09-01 a 2019-11-30 - PTRF - Cheque  - FECHADO'


def test_meta_modelo(fechamento_periodo):
    assert fechamento_periodo._meta.verbose_name == 'Fechamento de período'
    assert fechamento_periodo._meta.verbose_name_plural == 'Fechamentos de períodos'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[FechamentoPeriodo]


def test_calculo_saldo_reprogramado_capital(fechamento_periodo):
    assert fechamento_periodo.saldo_reprogramado_capital == 300


def test_calculo_saldo_reprogramado_custeio(fechamento_periodo):
    assert fechamento_periodo.saldo_reprogramado_custeio == 600


def test_calculo_saldo_anterior(fechamento_periodo):
    assert fechamento_periodo.saldo_anterior == 300


def test_calculo_saldo_anterior_custeio(fechamento_periodo):
    assert fechamento_periodo.saldo_anterior_custeio == 200


def test_calculo_saldo_anterior_capital(fechamento_periodo):
    assert fechamento_periodo.saldo_anterior_capital == 100


def test_calculo_total_receitas(fechamento_periodo):
    assert fechamento_periodo.total_receitas == 3000


def test_calculo_total_despesas(fechamento_periodo):
    assert fechamento_periodo.total_despesas == 2400


def test_calculo_saldo_reprogramado(fechamento_periodo):
    assert fechamento_periodo.saldo_reprogramado == 900
