import pytest

from sme_ptrf_apps.core.services.dados_demo_financeiro_service import gerar_dados_demonstrativo_financeiro

pytestmark = pytest.mark.django_db


def test_deve_gerar_dados_para_demonstrativo_financeiro_da_prestacao_de_contas(
    dem_fin_conta_associacao_cheque,
    dem_fin_acao_associacao_ptrf,
    dem_fin_receita_estorno_100_custeio_conferida,
    dem_fin_receita_livre_conferida,
    dem_fin_rateio_despesa,
    dem_fin_observacao_conciliacao_2019_2,
    dem_fin_prestacao_conta_2019_2,
    dem_fin_fechamento_2019_2,
):

    prestacao = dem_fin_prestacao_conta_2019_2
    periodo = prestacao.periodo
    acoes = prestacao.associacao.acoes.filter(status="ATIVA")
    contas = prestacao.associacao.contas.filter(status="ATIVA")

    dados_demonstrativo = gerar_dados_demonstrativo_financeiro(
        "usuarioteste",
        acoes,
        periodo,
        contas[0],
        prestacao,
        dem_fin_observacao_conciliacao_2019_2,
        previa=False
    )

    assert dados_demonstrativo == {}
