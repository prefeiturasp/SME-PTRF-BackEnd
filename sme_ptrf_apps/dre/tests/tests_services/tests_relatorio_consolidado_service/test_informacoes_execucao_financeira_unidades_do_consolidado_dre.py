import pytest
from sme_ptrf_apps.dre.services.relatorio_consolidado_service import informacoes_execucao_financeira_unidades_do_consolidado_dre

pytestmark = pytest.mark.django_db


def test_informacoes_execucao_financeira_unidades_do_consolidado_dre_conta_sem_movimentacao_valores_zerados(
    dre_teste_service_consolidado_dre,
    associacao_teste_service,
    conta_associacao_teste_service_02_inicio_2022_1,
    periodo_teste_service_consolidado_dre,
    prestacao_conta_aprovada_ressalvas_consolidado_dre_retificado
):
    informacoes = informacoes_execucao_financeira_unidades_do_consolidado_dre(
        dre_teste_service_consolidado_dre,
        periodo_teste_service_consolidado_dre,
    )

    valores = informacoes[0]["por_tipo_de_conta"][0]["valores"]

    assert valores["saldo_reprogramado_periodo_anterior_custeio"] == 0
    assert valores["saldo_reprogramado_periodo_anterior_capital"] == 0
    assert valores["saldo_reprogramado_periodo_anterior_livre"] == 0
    assert valores["saldo_reprogramado_periodo_anterior_total"] == 0
    assert valores["repasses_previstos_sme_custeio"] == 0
    assert valores["repasses_previstos_sme_capital"] == 0
    assert valores["repasses_previstos_sme_livre"] == 0
    assert valores["repasses_previstos_sme_total"] == 0
    assert valores["repasses_no_periodo_custeio"] == 0
    assert valores["repasses_no_periodo_capital"] == 0
    assert valores["repasses_no_periodo_livre"] == 0
    assert valores["repasses_no_periodo_total"] == 0
    assert valores["receitas_rendimento_no_periodo_custeio"] == 0
    assert valores["receitas_rendimento_no_periodo_capital"] == 0
    assert valores["receitas_rendimento_no_periodo_livre"] == 0
    assert valores["receitas_rendimento_no_periodo_total"] == 0
    assert valores["receitas_devolucao_no_periodo_custeio"] == 0
    assert valores["receitas_devolucao_no_periodo_capital"] == 0
    assert valores["receitas_devolucao_no_periodo_livre"] == 0
    assert valores["receitas_devolucao_no_periodo_total"] == 0
    assert valores["demais_creditos_no_periodo_custeio"] == 0
    assert valores["demais_creditos_no_periodo_capital"] == 0
    assert valores["demais_creditos_no_periodo_livre"] == 0
    assert valores["demais_creditos_no_periodo_total"] == 0
    assert valores["receitas_totais_no_periodo_custeio"] == 0
    assert valores["receitas_totais_no_periodo_capital"] == 0
    assert valores["receitas_totais_no_periodo_livre"] == 0
    assert valores["receitas_totais_no_periodo_total"] == 0
    assert valores["despesas_no_periodo_custeio"] == 0
    assert valores["despesas_no_periodo_capital"] == 0
    assert valores["despesas_no_periodo_total"] == 0
    assert valores["saldo_reprogramado_proximo_periodo_custeio"] == 0
    assert valores["saldo_reprogramado_proximo_periodo_capital"] == 0
    assert valores["saldo_reprogramado_proximo_periodo_livre"] == 0
    assert valores["saldo_reprogramado_proximo_periodo_total"] == 0
    assert valores["devolucoes_ao_tesouro_no_periodo_total"] == 0
