import pytest
from ...models import ConsolidadoDRE, RelatorioConsolidadoDRE
from sme_ptrf_apps.core.models import TipoConta
from ...services.consolidado_dre_service import concluir_consolidado_dre, _criar_documentos, status_consolidado_dre

pytestmark = pytest.mark.django_db


def test_get_status_consolidado_dre_nao_gerado(
    consolidado_dre_teste_service_consolidado_dre,
    dre_teste_service_consolidado_dre,
    periodo_teste_service_consolidado_dre
):
    result = status_consolidado_dre(dre_teste_service_consolidado_dre, periodo_teste_service_consolidado_dre)

    resultado_esperado = {
        'pcs_em_analise': False,
        'status_geracao': 'NAO_GERADOS',
        'status_txt': 'Análise de prestações de contas das associações completa. Documentos não gerados.',
        'cor_idx': 2,
        'status_arquivo': 'Documentos não gerados'
    }

    assert result == resultado_esperado


def test_get_status_consolidado_dre_gerados_totais(
    consolidado_dre_teste_service_consolidado_dre_status_gerados_totais,
    dre_teste_service_consolidado_dre,
    periodo_teste_service_consolidado_dre
):
    result = status_consolidado_dre(dre_teste_service_consolidado_dre, periodo_teste_service_consolidado_dre)

    resultado_esperado = {
        'cor_idx': 3,
        'pcs_em_analise': False,
        'status_arquivo': result['status_arquivo'],
        'status_geracao': 'GERADOS_TOTAIS',
        'status_txt': 'Análise de prestações de contas das associações completa. Documentos finais gerados.'
    }

    assert result == resultado_esperado
