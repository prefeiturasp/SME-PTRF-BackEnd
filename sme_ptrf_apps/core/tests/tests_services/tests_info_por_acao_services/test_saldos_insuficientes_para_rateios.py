from decimal import Decimal
import pytest

from datetime import date
from sme_ptrf_apps.core.models.acao_associacao import AcaoAssociacao
from sme_ptrf_apps.core.models.fechamento_periodo import FechamentoPeriodo

from sme_ptrf_apps.despesas.models.rateio_despesa import RateioDespesa
from ....services import saldos_insuficientes_para_rateios

pytestmark = pytest.mark.django_db

@pytest.fixture
def dados_em_comum_testes_saldos_insuficientes_para_rateios(associacao_factory, conta_associacao_factory, despesa_factory, rateio_despesa_factory, periodo_factory, fechamento_periodo_factory, tipo_conta_factory, prestacao_conta_factory, acao_associacao_factory, acao_factory):
    associacao = associacao_factory.create()

    acao = acao_factory.create(nome="PTRF Básico", aceita_capital=True, aceita_custeio=True, aceita_livre=True)
    acao_associacao = acao_associacao_factory.create(associacao=associacao, acao=acao)

    tipo_conta = tipo_conta_factory.create(nome="Caixa")
    conta = conta_associacao_factory.create(tipo_conta=tipo_conta, associacao=associacao)

    periodo_anterior = periodo_factory.create(
        referencia="2021.3",
        data_inicio_realizacao_despesas=date(2021, 10, 1),
        data_fim_realizacao_despesas=date(2021, 12, 31),
    )
    periodo = periodo_factory.create(
        periodo_anterior=periodo_anterior,
        referencia="2022.1",
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 4, 30),
    )
    
    despesa = despesa_factory.create(associacao=associacao, data_transacao=date(2021,10,2), data_documento=date(2021,10,2))
    
    pc = prestacao_conta_factory.create(periodo=periodo_anterior, associacao=associacao)
    
    return associacao, acao_associacao, conta, periodo, periodo_anterior, despesa, pc

def test_valor_conta_insuficiente(dados_em_comum_testes_saldos_insuficientes_para_rateios, rateio_despesa_factory, fechamento_periodo_factory):
    associacao, acao_associacao, conta, periodo, periodo_anterior, despesa, pc = dados_em_comum_testes_saldos_insuficientes_para_rateios
    
    rateios = list()
    rateio = rateio_despesa_factory.create(despesa=despesa, associacao=associacao, conta_associacao=conta, valor_rateio=Decimal(9000), valor_original=Decimal(9000), aplicacao_recurso="CUSTEIO",acao_associacao=acao_associacao, status="COMPLETO")
    
    rateios.append({'id': rateio.id, 'despesa': rateio.despesa, 'conta_associacao': rateio.conta_associacao.uuid, 'acao_associacao': rateio.acao_associacao.uuid, 'aplicacao_recurso': "CUSTEIO", 'valor_rateio': rateio.valor_rateio})
    
    fechamento_periodo_factory.create(prestacao_conta=pc, periodo=periodo_anterior, associacao=associacao, conta_associacao=conta, acao_associacao=acao_associacao, fechamento_anterior=None, total_receitas_capital=0, total_despesas_capital=0, total_receitas_custeio=500, total_despesas_custeio=9000, status="FECHADO")
    
    response = saldos_insuficientes_para_rateios(rateios=rateios, periodo=periodo, exclude_despesa=despesa.uuid)
    
    assert response['tipo_saldo'] == "CONTA"
    assert response['saldos_insuficientes'][0]['conta'] == "Caixa"
    assert response['saldos_insuficientes'][0]['saldo_disponivel'] == Decimal(500)
    assert response['saldos_insuficientes'][0]['total_rateios'] == Decimal(9000)
    
def test_valor_acao_insuficiente(dados_em_comum_testes_saldos_insuficientes_para_rateios, rateio_despesa_factory, fechamento_periodo_factory, acao_associacao_factory, acao_factory):
    associacao, acao_associacao, conta, periodo, periodo_anterior, despesa, pc = dados_em_comum_testes_saldos_insuficientes_para_rateios

    rateios = list()
    rateio = rateio_despesa_factory.create(despesa=despesa, associacao=associacao, conta_associacao=conta, valor_rateio=Decimal(10000), valor_original=Decimal(10000), aplicacao_recurso="CUSTEIO",acao_associacao=acao_associacao, status="COMPLETO", conferido="True")
    
    rateios.append({'id': rateio.id, 'despesa': rateio.despesa, 'conta_associacao': rateio.conta_associacao.uuid, 'acao_associacao': rateio.acao_associacao.uuid, 'aplicacao_recurso': "CUSTEIO", 'valor_rateio': rateio.valor_rateio})
    
    fechamento_periodo_factory.create(prestacao_conta=pc, periodo=periodo_anterior, associacao=associacao, conta_associacao=conta, acao_associacao=acao_associacao, fechamento_anterior=None, total_receitas_capital=0, total_despesas_capital=0, total_receitas_custeio=500, total_despesas_custeio=10000, status="FECHADO")
    
    outra_acao = acao_factory.create(nome="Role Cultural", aceita_capital=True, aceita_custeio=True, aceita_livre=True)
    outra_acao_associacao = acao_associacao_factory.create(associacao=associacao, acao=outra_acao)
    
    fechamento_periodo_factory.create(prestacao_conta=pc, periodo=periodo_anterior, associacao=associacao, conta_associacao=conta, acao_associacao=outra_acao_associacao, fechamento_anterior=None, total_receitas_capital=200000, total_despesas_capital=0, total_receitas_custeio=200000, total_despesas_custeio=0, status="FECHADO")
    
    response = saldos_insuficientes_para_rateios(rateios=rateios, periodo=periodo, exclude_despesa=despesa.uuid)
    
    assert response['tipo_saldo'] == "ACAO"
    assert response['saldos_insuficientes'][0]['conta'] == "Caixa"
    assert response['saldos_insuficientes'][0]['aplicacao'] == "CUSTEIO"
    assert response['saldos_insuficientes'][0]['saldo_disponivel'] == Decimal(500)
    assert response['saldos_insuficientes'][0]['total_rateios'] == Decimal(10000)
    
    
def test_valor_aplicacao_insuficiente(dados_em_comum_testes_saldos_insuficientes_para_rateios, rateio_despesa_factory, fechamento_periodo_factory):
    associacao, acao_associacao, conta, periodo, periodo_anterior, despesa, pc = dados_em_comum_testes_saldos_insuficientes_para_rateios

    rateios = list()
    rateio = rateio_despesa_factory.create(despesa=despesa, associacao=associacao, conta_associacao=conta, valor_rateio=Decimal(10000), valor_original=Decimal(10000), aplicacao_recurso="CAPITAL",acao_associacao=acao_associacao, status="COMPLETO", conferido="True")
    
    rateios.append({'id': rateio.id, 'despesa': rateio.despesa, 'conta_associacao': rateio.conta_associacao.uuid, 'acao_associacao': rateio.acao_associacao.uuid, 'aplicacao_recurso': "CAPITAL", 'valor_rateio': rateio.valor_rateio})
    
    fechamento_periodo_factory.create(prestacao_conta=pc, periodo=periodo_anterior, associacao=associacao, conta_associacao=conta, acao_associacao=acao_associacao, fechamento_anterior=None, total_receitas_capital=0, total_despesas_capital=10000, total_receitas_custeio=50000, total_despesas_custeio=0, status="FECHADO")
    
    response = saldos_insuficientes_para_rateios(rateios=rateios, periodo=periodo, exclude_despesa=despesa.uuid)
    
    assert response['tipo_saldo'] == "ACAO"
    assert response['saldos_insuficientes'][0]['conta'] == "Caixa"
    assert response['saldos_insuficientes'][0]['aplicacao'] == "CAPITAL"
    assert response['saldos_insuficientes'][0]['saldo_disponivel'] == Decimal(0)
    assert response['saldos_insuficientes'][0]['total_rateios'] == Decimal(10000)

def test_uso_valor_livre_aplicacao(dados_em_comum_testes_saldos_insuficientes_para_rateios, rateio_despesa_factory, fechamento_periodo_factory, acao_associacao_factory, acao_factory):
    associacao, acao_associacao, conta, periodo, periodo_anterior, despesa, pc = dados_em_comum_testes_saldos_insuficientes_para_rateios

    rateios = list()
    rateio_custeio = rateio_despesa_factory.create(despesa=despesa, associacao=associacao, conta_associacao=conta, valor_rateio=Decimal(10000), valor_original=Decimal(10000), aplicacao_recurso="CUSTEIO",acao_associacao=acao_associacao, status="COMPLETO", conferido="True")
    rateio_capital = rateio_despesa_factory.create(despesa=despesa, associacao=associacao, conta_associacao=conta, valor_rateio=Decimal(6000), valor_original=Decimal(6000), aplicacao_recurso="CAPITAL",acao_associacao=acao_associacao, status="COMPLETO", conferido="True")
    
    rateios.append({'id': rateio_custeio.id, 'despesa': rateio_custeio.despesa, 'conta_associacao': rateio_custeio.conta_associacao.uuid, 'acao_associacao': rateio_custeio.acao_associacao.uuid, 'aplicacao_recurso': rateio_custeio.aplicacao_recurso, 'valor_rateio': rateio_custeio.valor_rateio})
    
    rateios.append({'id': rateio_capital.id, 'despesa': rateio_capital.despesa, 'conta_associacao': rateio_capital.conta_associacao.uuid, 'acao_associacao': rateio_capital.acao_associacao.uuid, 'aplicacao_recurso': rateio_capital.aplicacao_recurso, 'valor_rateio': rateio_capital.valor_rateio})
    
    fechamento_periodo_factory.create(prestacao_conta=pc, periodo=periodo_anterior, associacao=associacao, conta_associacao=conta, acao_associacao=acao_associacao, fechamento_anterior=None, total_receitas_capital=5000, total_despesas_capital=6000, total_receitas_custeio=5000, total_despesas_custeio=10000, total_receitas_livre=6000, status="FECHADO")
    
    outra_acao = acao_factory.create(nome="Role Cultural", aceita_capital=True, aceita_custeio=True, aceita_livre=True)
    outra_acao_associacao = acao_associacao_factory.create(associacao=associacao, acao=outra_acao)
    
    fechamento_periodo_factory.create(prestacao_conta=pc, periodo=periodo_anterior, associacao=associacao, conta_associacao=conta, acao_associacao=outra_acao_associacao, fechamento_anterior=None, total_receitas_capital=200000, total_despesas_capital=0, total_receitas_custeio=200000, total_despesas_custeio=0, status="FECHADO")
    
    response = saldos_insuficientes_para_rateios(rateios=rateios, periodo=periodo, exclude_despesa=despesa.uuid)
    
    assert response['tipo_saldo'] == "ACAO"
    assert response['saldos_insuficientes'] == []
    
def test_uso_valor_livre_aplicacao_em_um_rateio_mas_insuficiente_para_o_outro(dados_em_comum_testes_saldos_insuficientes_para_rateios, rateio_despesa_factory, fechamento_periodo_factory, acao_associacao_factory, acao_factory):
    associacao, acao_associacao, conta, periodo, periodo_anterior, despesa, pc = dados_em_comum_testes_saldos_insuficientes_para_rateios

    rateios = list()
    rateio_custeio = rateio_despesa_factory.create(despesa=despesa, associacao=associacao, conta_associacao=conta, valor_rateio=Decimal(10000), valor_original=Decimal(10000), aplicacao_recurso="CUSTEIO",acao_associacao=acao_associacao, status="COMPLETO", conferido="True")
    rateio_capital = rateio_despesa_factory.create(despesa=despesa, associacao=associacao, conta_associacao=conta, valor_rateio=Decimal(6000), valor_original=Decimal(6000), aplicacao_recurso="CAPITAL",acao_associacao=acao_associacao, status="COMPLETO", conferido="True")
    
    rateios.append({'id': rateio_custeio.id, 'despesa': rateio_custeio.despesa, 'conta_associacao': rateio_custeio.conta_associacao.uuid, 'acao_associacao': rateio_custeio.acao_associacao.uuid, 'aplicacao_recurso': rateio_custeio.aplicacao_recurso, 'valor_rateio': rateio_custeio.valor_rateio})
    
    rateios.append({'id': rateio_capital.id, 'despesa': rateio_capital.despesa, 'conta_associacao': rateio_capital.conta_associacao.uuid, 'acao_associacao': rateio_capital.acao_associacao.uuid, 'aplicacao_recurso': rateio_capital.aplicacao_recurso, 'valor_rateio': rateio_capital.valor_rateio})
    
    fechamento_periodo_factory.create(prestacao_conta=pc, periodo=periodo_anterior, associacao=associacao, conta_associacao=conta, acao_associacao=acao_associacao, fechamento_anterior=None, total_receitas_capital=5000, total_despesas_capital=6000, total_receitas_custeio=5000, total_despesas_custeio=10000, total_receitas_livre=5000, status="FECHADO")
    
    outra_acao = acao_factory.create(nome="Role Cultural", aceita_capital=True, aceita_custeio=True, aceita_livre=True)
    outra_acao_associacao = acao_associacao_factory.create(associacao=associacao, acao=outra_acao)
    
    fechamento_periodo_factory.create(prestacao_conta=pc, periodo=periodo_anterior, associacao=associacao, conta_associacao=conta, acao_associacao=outra_acao_associacao, fechamento_anterior=None, total_receitas_capital=200000, total_despesas_capital=0, total_receitas_custeio=200000, total_despesas_custeio=0, status="FECHADO")
    
    response = saldos_insuficientes_para_rateios(rateios=rateios, periodo=periodo, exclude_despesa=despesa.uuid)
    
    assert response['tipo_saldo'] == "ACAO"
    assert response['saldos_insuficientes'][0]['conta'] == "Caixa"
    assert response['saldos_insuficientes'][0]['aplicacao'] == "CUSTEIO"
    assert response['saldos_insuficientes'][0]['saldo_disponivel'] == Decimal(9000)
    assert response['saldos_insuficientes'][0]['total_rateios'] == Decimal(10000)


