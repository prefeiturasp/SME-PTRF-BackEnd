import pytest
from datetime import date
from uuid import UUID
from waffle.testutils import override_flag

from sme_ptrf_apps.core.services.dados_relatorio_acertos_service import gerar_dados_relatorio_acertos

pytestmark = pytest.mark.django_db

@override_flag('ajustes-despesas-anteriores', active=True)
def test_dados_relatorios_acertos_despesas_periodos_anteriores(solicitacao_acerto_lancamento_factory, tipo_acerto_lancamento_factory, analise_lancamento_prestacao_conta_factory, despesa_factory, periodo_factory, associacao_factory, prestacao_conta_factory, analise_prestacao_conta_factory, rateio_despesa_factory, conta_associacao_factory, acao_associacao_factory, tipo_transacao_factory):
    
    periodo_inicial = periodo_factory.create(referencia="2023.1", data_inicio_realizacao_despesas=date(2023,1,1), data_fim_realizacao_despesas=date(2023,4,20))
    periodo = periodo_factory.create(referencia="2023.2", data_inicio_realizacao_despesas=date(2023,4,21), data_fim_realizacao_despesas=date(2023,6,20))
    periodo_pc = periodo_factory.create(referencia="2023.3", data_inicio_realizacao_despesas=date(2023,6,21), data_fim_realizacao_despesas=date(2023,12,20))
    
    associacao = associacao_factory.create(periodo_inicial=periodo_inicial)
    
    tipo_transacao = tipo_transacao_factory.create(nome="Cartão")
    
    despesa = despesa_factory.create(tipo_transacao=tipo_transacao, associacao=associacao, data_transacao=date(2023,5,20), data_documento=date(2023,5,20), eh_despesa_reconhecida_pela_associacao=True, status="COMPLETO", valor_total=30, eh_despesa_sem_comprovacao_fiscal=True)
    
    conta = conta_associacao_factory.create(associacao=associacao)
    
    acao_associacao = acao_associacao_factory.create(associacao=associacao)
    
    rateio = rateio_despesa_factory.create(despesa=despesa, associacao=associacao, conta_associacao=conta, acao_associacao=acao_associacao, status="COMPLETO", valor_rateio=30, valor_original=30, eh_despesa_sem_comprovacao_fiscal=True, periodo_conciliacao=periodo_pc, conferido=True, aplicacao_recurso="CUSTEIO")
    
    prestacao_conta = prestacao_conta_factory.create(periodo=periodo_pc, associacao=associacao, status="EM_ANALISE")
    
    analise_prestacao_conta = analise_prestacao_conta_factory(prestacao_conta=prestacao_conta)
    
    analise_lancamento_prestacao_conta = analise_lancamento_prestacao_conta_factory.create(analise_prestacao_conta=analise_prestacao_conta, despesa=despesa)
    
    tipo_acerto_lancamento = tipo_acerto_lancamento_factory.create(categoria="CONCILIACAO_LANCAMENTO")
    
    solicitaco_acerto = solicitacao_acerto_lancamento_factory.create(analise_lancamento=analise_lancamento_prestacao_conta, tipo_acerto=tipo_acerto_lancamento)
    
    dados = gerar_dados_relatorio_acertos(analise_prestacao_conta=analise_prestacao_conta, previa=False)
    
    solicitacoes_de_ajuste = dados['dados_despesas_periodos_anteriores'][0]['lancamentos'][0]['analise_lancamento']['solicitacoes_de_ajuste_da_analise']
    solicitacoes_de_ajuste_por_categoria = solicitacoes_de_ajuste['solicitacoes_acerto_por_categoria'][0]
    tipo_acerto = solicitacoes_de_ajuste_por_categoria['acertos'][0]['tipo_acerto']
    
    assert UUID(solicitacoes_de_ajuste['analise_lancamento']) == analise_lancamento_prestacao_conta.uuid
    assert tipo_acerto['nome'] == tipo_acerto_lancamento.nome
    assert tipo_acerto['categoria'] == "CONCILIACAO_LANCAMENTO"
    assert UUID(solicitacoes_de_ajuste_por_categoria['despesa']) == despesa.uuid
    assert solicitacoes_de_ajuste_por_categoria['categoria'] == "CONCILIACAO_LANCAMENTO"
    assert solicitacoes_de_ajuste_por_categoria['acertos'][0]['detalhamento'] == solicitaco_acerto.detalhamento
    
    