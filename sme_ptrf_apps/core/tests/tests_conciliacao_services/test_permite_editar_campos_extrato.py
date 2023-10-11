import pytest
from datetime import date
from freezegun import freeze_time
from sme_ptrf_apps.core.models.periodo import Periodo
from sme_ptrf_apps.core.services.conciliacao_services import permite_editar_campos_extrato
from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta

pytestmark = pytest.mark.django_db

@freeze_time('2019-03-25 10:10:10')
def test_permite_editar_campos_extrato_no_periodo_em_andamento_com_conta_criada_no_periodo(associacao_factory, conta_associacao_factory, periodo_factory, prestacao_conta_factory):
    
    associacao = associacao_factory.create()
    
    conta = conta_associacao_factory.create(associacao=associacao, data_inicio=date(2019, 2, 2))

    periodo_aberto = periodo_factory.create(
        referencia="2019.1",
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 3, 31),
    )
    
    permite_editar = permite_editar_campos_extrato(associacao, periodo_aberto, conta)
    
    prestacao_conta = prestacao_conta_factory.create(periodo=periodo_aberto, associacao=associacao)
    
    assert prestacao_conta
    assert periodo_aberto == Periodo.da_data(conta.data_inicio)
    assert not periodo_aberto.encerrado
    assert permite_editar == True
    
@freeze_time('2019-04-01 10:10:10')
def test_permite_editar_campos_extrato_no_periodo_finalizado_com_conta_criada_no_periodo_e_documentos_pendentes_de_geracao(associacao_factory, conta_associacao_factory, periodo_factory, prestacao_conta_factory):
    
    associacao = associacao_factory.create()
    
    conta = conta_associacao_factory.create(associacao=associacao, data_inicio=date(2019, 2, 2))

    periodo_encerrado = periodo_factory.create(
        referencia="2019.1",
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 3, 31),
    )
    
    prestacao_conta = prestacao_conta_factory.create(periodo=periodo_encerrado, associacao=associacao, status=PrestacaoConta.STATUS_NAO_APRESENTADA)
    
    permite_editar = permite_editar_campos_extrato(associacao, periodo_encerrado, conta)
    
    assert prestacao_conta
    assert periodo_encerrado == Periodo.da_data(conta.data_inicio)
    assert periodo_encerrado.encerrado
    assert permite_editar == True
    
@freeze_time('2019-04-01 10:10:10')
def test_permite_editar_campos_extrato_no_periodo_finalizado_com_conta_criada_no_periodo_e_pc_devolvida_para_ajustes(associacao_factory, conta_associacao_factory, periodo_factory, prestacao_conta_factory):
    
    associacao = associacao_factory.create()
    
    conta = conta_associacao_factory.create(associacao=associacao, data_inicio=date(2019, 2, 2))

    periodo_encerrado = periodo_factory.create(
        referencia="2019.1",
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 3, 31),
    )
    
    prestacao_conta = prestacao_conta_factory.create(periodo=periodo_encerrado, associacao=associacao, status=PrestacaoConta.STATUS_DEVOLVIDA)
    
    permite_editar = permite_editar_campos_extrato(associacao, periodo_encerrado, conta)
    
    assert prestacao_conta
    assert periodo_encerrado == Periodo.da_data(conta.data_inicio)
    assert periodo_encerrado.encerrado
    assert permite_editar == True