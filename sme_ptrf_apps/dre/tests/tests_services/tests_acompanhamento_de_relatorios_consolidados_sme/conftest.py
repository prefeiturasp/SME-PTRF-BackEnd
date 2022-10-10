import pytest
from model_bakery import baker
from sme_ptrf_apps.dre.models import ConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def dre_acompanhamento_de_relatorios_consolidados_dashboard_sem_consolidado_dre():
    return baker.make(
        'Unidade',
        codigo_eol='100000',
        tipo_unidade='DRE',
        nome='Dre Teste Model Consolidado Dre',
        sigla='S'
    )


@pytest.fixture
def dre_acompanhamento_de_relatorios_consolidados_dashboard_com_consolidado_dre():
    return baker.make(
        'Unidade',
        codigo_eol='100001',
        tipo_unidade='DRE',
        nome='Dre Teste Model Consolidado Dre',
        sigla='S'
    )


@pytest.fixture
def consolidado_dre_acompanhamento_de_relatorios_consolidados_dashboard_nao_publicado(
    periodo_teste_service_consolidado_dre,
    dre_teste_service_consolidado_dre
):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_service_consolidado_dre,
        periodo=periodo_teste_service_consolidado_dre,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS,
        status_sme=ConsolidadoDRE.STATUS_SME_NAO_PUBLICADO
    )

@pytest.fixture
def consolidado_dre_acompanhamento_de_relatorios_consolidados_dashboard_publicado(
    periodo_teste_service_consolidado_dre,
    dre_teste_service_consolidado_dre
):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_service_consolidado_dre,
        periodo=periodo_teste_service_consolidado_dre,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS,
        status_sme=ConsolidadoDRE.STATUS_SME_PUBLICADO
    )

@pytest.fixture
def consolidado_dre_acompanhamento_de_relatorios_consolidados_dashboard_publicado_outra_dre(
    periodo_teste_service_consolidado_dre,
    dre_acompanhamento_de_relatorios_consolidados_dashboard_com_consolidado_dre
):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_acompanhamento_de_relatorios_consolidados_dashboard_com_consolidado_dre,
        periodo=periodo_teste_service_consolidado_dre,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS,
        status_sme=ConsolidadoDRE.STATUS_SME_PUBLICADO
    )
