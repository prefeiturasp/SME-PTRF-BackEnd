import pytest
from datetime import date
from sme_ptrf_apps.core.services.dados_demo_financeiro_service import gerar_dados_demonstrativo_financeiro
from sme_ptrf_apps.despesas.fixtures.factories import RateioDespesaFactory, DespesaFactory
from sme_ptrf_apps.core.fixtures.factories import (PeriodoFactory, ContaAssociacaoFactory, PrestacaoContaFactory,
                                                   AssociacaoFactory, AcaoFactory, AcaoAssociacaoFactory)
pytestmark = pytest.mark.django_db


def test_despesas_demonstradas_despesa_conciliada_no_periodo(
    associacao,
    df_conta_associacao_cartao,
    df_periodo_2020_1,
    df_prestacao_conta_2020_1,
    df_fechamento_periodo_2020_1,
    df_rateio_despesa_2020_1_cartao_ptrf_custeio_conferido_em_2020_1
):
    acoes = associacao.acoes.filter(status='ATIVA')
    resultado = gerar_dados_demonstrativo_financeiro(
        usuario='teste',
        acoes=acoes,
        periodo=df_periodo_2020_1,
        conta_associacao=df_conta_associacao_cartao,
        prestacao=df_prestacao_conta_2020_1,
        observacao_conciliacao="",
        previa=False,
    )

    assert resultado['despesas_demonstradas']['valor_total'] == 100
    assert resultado['despesas_nao_demonstradas']['valor_total'] == 0
    assert resultado['despesas_anteriores_nao_demonstradas']['valor_total'] == 0


def test_despesas_demonstradas_despesa_conciliada_em_periodo_futuro(
    associacao,
    df_conta_associacao_cartao,
    df_periodo_2020_1,
    df_prestacao_conta_2020_1,
    df_fechamento_periodo_2020_1,
    df_rateio_despesa_2020_1_cartao_ptrf_custeio_conferido_em_2020_2
):
    acoes = associacao.acoes.filter(status='ATIVA')
    resultado = gerar_dados_demonstrativo_financeiro(
        usuario='teste',
        acoes=acoes,
        periodo=df_periodo_2020_1,
        conta_associacao=df_conta_associacao_cartao,
        prestacao=df_prestacao_conta_2020_1,
        observacao_conciliacao="",
        previa=False,
    )

    assert resultado['despesas_demonstradas']['valor_total'] == 0
    assert resultado['despesas_nao_demonstradas']['valor_total'] == 100
    assert resultado['despesas_anteriores_nao_demonstradas']['valor_total'] == 0


def test_despesas_demonstradas_despesa_anteriores_conciliadas_em_periodo_futuro(
    associacao,
    df_conta_associacao_cartao,
    df_periodo_2020_1,
    df_prestacao_conta_2020_1,
    df_fechamento_periodo_2020_1,
    df_rateio_despesa_2019_2_cartao_ptrf_custeio_conferido_em_2021_1
):
    acoes = associacao.acoes.filter(status='ATIVA')
    resultado = gerar_dados_demonstrativo_financeiro(
        usuario='teste',
        acoes=acoes,
        periodo=df_periodo_2020_1,
        conta_associacao=df_conta_associacao_cartao,
        prestacao=df_prestacao_conta_2020_1,
        observacao_conciliacao="",
        previa=False,
    )

    assert resultado['despesas_demonstradas']['valor_total'] == 0, "Não deveria estar em demonstradas"
    assert resultado['despesas_nao_demonstradas']['valor_total'] == 0, "Não deveria estar em não demonstradas"
    assert resultado['despesas_anteriores_nao_demonstradas']['valor_total'] == 100, "Deveria estar em anteriores não demonstradas"


def test_despesas_demonstradas_despesa_anteriores_nao_conciliadas(
    associacao,
    df_conta_associacao_cartao,
    df_periodo_2020_1,
    df_prestacao_conta_2020_1,
    df_fechamento_periodo_2020_1,
    df_rateio_despesa_2019_2_cartao_ptrf_custeio_nao_conferido
):
    acoes = associacao.acoes.filter(status='ATIVA')
    resultado = gerar_dados_demonstrativo_financeiro(
        usuario='teste',
        acoes=acoes,
        periodo=df_periodo_2020_1,
        conta_associacao=df_conta_associacao_cartao,
        prestacao=df_prestacao_conta_2020_1,
        observacao_conciliacao="",
        previa=False,
    )

    assert resultado['despesas_demonstradas']['valor_total'] == 0, "Não deveria estar em demonstradas"
    assert resultado['despesas_nao_demonstradas']['valor_total'] == 0, "Não deveria estar em não demonstradas"
    assert resultado['despesas_anteriores_nao_demonstradas']['valor_total'] == 100, "Deveria estar em anteriores não demonstradas"

def test_despesas_demonstradas_primeira_pc_associacao():
    periodo_2022_2 = PeriodoFactory(data_inicio_realizacao_despesas=date(2022, 12, 31))
    associacao = AssociacaoFactory(periodo_inicial=periodo_2022_2)
    periodo = PeriodoFactory(periodo_anterior=periodo_2022_2, data_inicio_realizacao_despesas=date(2023, 1, 1))
    pc = PrestacaoContaFactory(periodo=periodo, associacao=associacao)
    conta_associacao = ContaAssociacaoFactory(associacao=associacao)
    acao = AcaoFactory()
    acao_associacao = AcaoAssociacaoFactory(acao=acao, associacao=associacao)
    despesa_1 = DespesaFactory(data_transacao=date(2023, 1, 1), valor_total=50)
    rateio_1 = RateioDespesaFactory(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_1,
        associacao=associacao,
        valor_rateio=50,
        conferido=True,
        update_conferido=True,
        periodo_conciliacao=periodo
    )
    despesa_2 = DespesaFactory(data_transacao=date(2023, 1, 1), valor_total=100)
    rateio_2 = RateioDespesaFactory(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_2,
        associacao=associacao,
        valor_rateio=100,
        conferido=True,
        update_conferido=True,
        periodo_conciliacao=periodo
    )
    despesa_3_periodo_anterior = DespesaFactory(data_transacao=date(2018, 1, 1), valor_total=100)
    rateio_3_periodo_anterior = RateioDespesaFactory(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_3_periodo_anterior,
        associacao=associacao,
        valor_rateio=100,
        conferido=True,
        update_conferido=True,
        periodo_conciliacao=periodo
    )
    resultado = gerar_dados_demonstrativo_financeiro(
        usuario='teste',
        acoes=[acao_associacao],
        periodo=periodo,
        conta_associacao=conta_associacao,
        prestacao=pc,
        observacao_conciliacao="",
        previa=False,
    )

    assert len(resultado['despesas_demonstradas']['linhas']) == 3
    assert resultado['despesas_demonstradas']['valor_total'] == 250.00

def test_despesas_demonstradas_segunda_pc_associacao():
    periodo_2022_2 = PeriodoFactory(data_inicio_realizacao_despesas=date(2022, 12, 31))
    periodo_2023_1 = PeriodoFactory(
        periodo_anterior=periodo_2022_2,
        data_inicio_realizacao_despesas=date(2023, 1, 1),
        data_fim_realizacao_despesas=date(2023, 6, 1)
    )
    periodo_2023_2 = PeriodoFactory(
        periodo_anterior=periodo_2023_1,
        data_inicio_realizacao_despesas=date(2023, 6, 2),
        data_fim_realizacao_despesas=date(2023, 12, 31)
    )
    associacao = AssociacaoFactory(periodo_inicial=periodo_2022_2)
    conta_associacao = ContaAssociacaoFactory(associacao=associacao)
    acao = AcaoFactory()
    acao_associacao = AcaoAssociacaoFactory(acao=acao, associacao=associacao)

    PrestacaoContaFactory(periodo=periodo_2023_1, associacao=associacao)
    despesa_1 = DespesaFactory(data_transacao=date(2023, 1, 1), valor_total=50)
    RateioDespesaFactory(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_1,
        associacao=associacao,
        valor_rateio=50,
        conferido=True,
        update_conferido=True,
        periodo_conciliacao=periodo_2023_1
    )

    pc_23_2 = PrestacaoContaFactory(periodo=periodo_2023_2, associacao=associacao)
    despesa_1_32_2 = DespesaFactory(data_transacao=date(2023, 6, 2), valor_total=100)
    RateioDespesaFactory(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_1_32_2,
        associacao=associacao,
        valor_rateio=100,
        conferido=True,
        update_conferido=True,
        periodo_conciliacao=periodo_2023_2
    )
    despesa_2_32_2 = DespesaFactory(data_transacao=date(2023, 6, 3), valor_total=80)
    RateioDespesaFactory(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_2_32_2,
        associacao=associacao,
        valor_rateio=80,
        conferido=True,
        update_conferido=True,
        periodo_conciliacao=periodo_2023_2
    )
    resultado = gerar_dados_demonstrativo_financeiro(
        usuario='teste',
        acoes=[acao_associacao],
        periodo=periodo_2023_2,
        conta_associacao=conta_associacao,
        prestacao=pc_23_2,
        observacao_conciliacao="",
        previa=False,
    )

    assert len(resultado['despesas_demonstradas']['linhas']) == 2
    assert resultado['despesas_demonstradas']['valor_total'] == 180.00
