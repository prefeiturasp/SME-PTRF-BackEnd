import pytest

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
