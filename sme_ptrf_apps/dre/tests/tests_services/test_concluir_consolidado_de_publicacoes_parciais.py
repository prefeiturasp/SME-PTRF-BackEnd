import pytest

from ...models import RelatorioConsolidadoDRE
from ...services.consolidado_dre_service import concluir_consolidado_de_publicacoes_parciais
from ...services.relatorio_consolidado_service import _criar_demonstrativo_execucao_fisico_financeiro, \
    _gerar_arquivos_demonstrativo_execucao_fisico_financeiro

pytestmark = pytest.mark.django_db


def test_consolidado_de_publicacoes_parciais_concluir(
    dre_teste_service_consolidado_dre,
    periodo_teste_service_consolidado_dre,
    retorna_username,
    associacao_teste_service,
    associacao_teste_service_02,
    prestacao_conta_reprovada_teste_service_publicada,
    prestacao_conta_aprovada_teste_service_pc_aprovada_info_pc,
    consolidado_dre_teste_service_consolidado_dre_versao_final,
    consolidado_dre_teste_service_consolidado_dre_versao_final_02,
    settings
):
    settings.CELERY_TASK_ALWAYS_EAGER = True

    concluir_consolidado_de_publicacoes_parciais(
        dre=dre_teste_service_consolidado_dre,
        periodo=periodo_teste_service_consolidado_dre,
        usuario=retorna_username,
    )

    assert RelatorioConsolidadoDRE.objects.filter(dre=dre_teste_service_consolidado_dre,
                                                  periodo=periodo_teste_service_consolidado_dre,
                                                  versao="CONSOLIDADA").exists()


def test_metodo_criar_demonstrativo_execucao_fisico_financeiro(
    dre_teste_service_consolidado_dre,
    periodo_teste_service_consolidado_dre,
    retorna_username,
    associacao_teste_service,
    associacao_teste_service_02,
    prestacao_conta_reprovada_teste_service_publicada,
    prestacao_conta_aprovada_teste_service_pc_aprovada_info_pc,
    consolidado_dre_teste_service_consolidado_dre_versao_final,
    consolidado_dre_teste_service_consolidado_dre_versao_final_02,
):
    parcial = {
        "parcial": False,
        "sequencia_de_publicacao_atual": None,
    }

    _criar_demonstrativo_execucao_fisico_financeiro(
        dre=dre_teste_service_consolidado_dre,
        periodo=periodo_teste_service_consolidado_dre,
        usuario=retorna_username,
        parcial=parcial,
        consolidado_dre=None,
        apenas_nao_publicadas=False,
        eh_consolidado_de_publicacoes_parciais=True,
    )

    assert RelatorioConsolidadoDRE.objects.filter(dre=dre_teste_service_consolidado_dre,
                                                  periodo=periodo_teste_service_consolidado_dre,
                                                  versao="CONSOLIDADA").exists()


def test_gerar_arquivos_demonstrativo_execucao_fisico_financeiro(
    dre_teste_service_consolidado_dre,
    periodo_teste_service_consolidado_dre,
    retorna_username,
    associacao_teste_service,
    associacao_teste_service_02,
    prestacao_conta_reprovada_teste_service_publicada,
    prestacao_conta_aprovada_teste_service_pc_aprovada_info_pc,
    consolidado_dre_teste_service_consolidado_dre_versao_final,
    consolidado_dre_teste_service_consolidado_dre_versao_final_02,
):
    parcial = {
        "parcial": False,
        "sequencia_de_publicacao_atual": None,
    }

    _gerar_arquivos_demonstrativo_execucao_fisico_financeiro(
        dre=dre_teste_service_consolidado_dre,
        periodo=periodo_teste_service_consolidado_dre,
        usuario=retorna_username,
        parcial=parcial,
        previa=False,
        consolidado_dre=None,
        apenas_nao_publicadas=False,
        eh_consolidado_de_publicacoes_parciais=True,
    )

    relatorio_consolidado = RelatorioConsolidadoDRE.objects.filter(
        dre=dre_teste_service_consolidado_dre,
        periodo=periodo_teste_service_consolidado_dre,
        versao="CONSOLIDADA"
    )

    assert relatorio_consolidado.exists()
    assert relatorio_consolidado.last().versao == "CONSOLIDADA"
