import pytest

from datetime import date
from model_bakery import baker

from sme_ptrf_apps.dre.models import ConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def vcs_periodo_2022_1():
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
    )


@pytest.fixture
def vcs_dre_ipiranga():
    return baker.make(
        'Unidade',
        codigo_eol='108500',
        tipo_unidade='DRE',
        nome='DRE IPIRANGA',
        sigla='I'
    )


@pytest.fixture
def vcs_consolidado_dre_ipiranga_2022_1(vcs_periodo_2022_1, vcs_dre_ipiranga):
    return baker.make(
        'ConsolidadoDRE',
        dre=vcs_dre_ipiranga,
        periodo=vcs_periodo_2022_1,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS,
        eh_parcial=False,
        sequencia_de_publicacao=0
    )


@pytest.fixture
def vcs_relatorio_dre_consolidado_gerado_total_desvinculado(vcs_periodo_2022_1, vcs_dre_ipiranga, tipo_conta_cartao, arquivo):
    return baker.make(
        'RelatorioConsolidadoDre',
        dre=vcs_dre_ipiranga,
        tipo_conta=tipo_conta_cartao,
        periodo=vcs_periodo_2022_1,
        arquivo=arquivo,
        status='GERADO_TOTAL',
        consolidado_dre=None,
    )
