import pytest
from datetime import date
from sme_ptrf_apps.core.services.dados_demo_financeiro_service import gerar_dados_demonstrativo_financeiro

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


def test_despesas_demonstradas_primeira_pc_associacao(periodo_factory, associacao_factory, prestacao_conta_factory, conta_associacao_factory, acao_factory, acao_associacao_factory, despesa_factory, rateio_despesa_factory):
    periodo_2022_2 = periodo_factory.create(data_inicio_realizacao_despesas=date(2022, 12, 31))
    associacao = associacao_factory.create(periodo_inicial=periodo_2022_2)
    periodo = periodo_factory.create(periodo_anterior=periodo_2022_2, data_inicio_realizacao_despesas=date(2023, 1, 1))
    pc = prestacao_conta_factory.create(periodo=periodo, associacao=associacao)
    conta_associacao = conta_associacao_factory.create(associacao=associacao)
    acao = acao_factory.create()
    acao_associacao = acao_associacao_factory(acao=acao, associacao=associacao)
    despesa_1 = despesa_factory.create(
        data_transacao=date(2023, 1, 1),
        valor_total=50,
        associacao=associacao
    )
    rateio_1 = rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_1,
        associacao=associacao,
        valor_rateio=50,
        conferido=True,
        update_conferido=True,
        periodo_conciliacao=periodo,
        aplicacao_recurso='CUSTEIO'
    )
    despesa_2 = despesa_factory.create(data_transacao=date(2023, 1, 1), valor_total=100, associacao=associacao)
    rateio_2 = rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_2,
        associacao=associacao,
        valor_rateio=100,
        conferido=True,
        update_conferido=True,
        periodo_conciliacao=periodo,
        aplicacao_recurso='CUSTEIO'
    )
    despesa_3_periodo_anterior = despesa_factory.create(
        data_transacao=date(2018, 1, 1), valor_total=100, associacao=associacao)
    rateio_3_periodo_anterior = rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_3_periodo_anterior,
        associacao=associacao,
        valor_rateio=100,
        conferido=True,
        update_conferido=True,
        periodo_conciliacao=periodo,
        aplicacao_recurso='CUSTEIO'
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

    assert len(resultado['despesas_demonstradas']['linhas']) == 2
    assert resultado['despesas_demonstradas']['valor_total'] == 150.00


def test_despesas_demonstradas_segunda_pc_associacao(associacao_factory, conta_associacao_factory, acao_factory, acao_associacao_factory, despesa_factory, prestacao_conta_factory, periodo_factory, rateio_despesa_factory):
    periodo_2022_2 = periodo_factory.create(data_inicio_realizacao_despesas=date(2022, 12, 31))
    periodo_2023_1 = periodo_factory.create(
        periodo_anterior=periodo_2022_2,
        data_inicio_realizacao_despesas=date(2023, 1, 1),
        data_fim_realizacao_despesas=date(2023, 6, 1)
    )
    periodo_2023_2 = periodo_factory.create(
        periodo_anterior=periodo_2023_1,
        data_inicio_realizacao_despesas=date(2023, 6, 2),
        data_fim_realizacao_despesas=date(2023, 12, 31)
    )
    associacao = associacao_factory.create(periodo_inicial=periodo_2022_2)
    conta_associacao = conta_associacao_factory.create(associacao=associacao)
    acao = acao_factory.create()
    acao_associacao = acao_associacao_factory.create(acao=acao, associacao=associacao)

    prestacao_conta_factory.create(periodo=periodo_2023_1, associacao=associacao)
    despesa_1 = despesa_factory.create(data_transacao=date(2023, 1, 1), valor_total=50, associacao=associacao)
    rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_1,
        associacao=associacao,
        valor_rateio=50,
        conferido=True,
        update_conferido=True,
        periodo_conciliacao=periodo_2023_1,
        aplicacao_recurso='CUSTEIO'
    )

    pc_23_2 = prestacao_conta_factory.create(periodo=periodo_2023_2, associacao=associacao)
    despesa_1_32_2 = despesa_factory.create(data_transacao=date(2023, 6, 2), valor_total=100, associacao=associacao)
    rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_1_32_2,
        associacao=associacao,
        valor_rateio=100,
        conferido=True,
        update_conferido=True,
        periodo_conciliacao=periodo_2023_2,
        aplicacao_recurso='CUSTEIO'
    )
    despesa_2_32_2 = despesa_factory.create(data_transacao=date(2023, 6, 3), valor_total=80, associacao=associacao)
    rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_2_32_2,
        associacao=associacao,
        valor_rateio=80,
        conferido=True,
        update_conferido=True,
        periodo_conciliacao=periodo_2023_2,
        aplicacao_recurso='CUSTEIO'
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
