import pytest

from sme_ptrf_apps.dre.services.consolidado_dre_service import Dashboard

pytestmark = pytest.mark.django_db


def test_acompanhamento_de_relatorios_consolidados_dashboard_1_nao_publicado(
    periodo_teste_service_consolidado_dre,
    consolidado_dre_acompanhamento_de_relatorios_consolidados_dashboard_nao_publicado

):
    acompanhamento_dashboard = Dashboard(periodo_teste_service_consolidado_dre).retorna_dashboard()

    resultado_esperado = {
        "cards": [
            {
                "titulo": "DREs sem relatório gerado",
                "quantidade_de_relatorios": 0,
                "status": "NAO_GERADO"
            },
            {
                "titulo": "Relatórios não publicados",
                "quantidade_de_relatorios": 1,
                "status": "NAO_PUBLICADO"
            },
            {
                "titulo": "Relatórios publicados",
                "quantidade_de_relatorios": 0,
                "status": "PUBLICADO"
            },
            {
                "titulo": "Relatórios em análise",
                "quantidade_de_relatorios": 0,
                "status": "EM_ANALISE"
            },
            {
                "titulo": "Relatórios devolvidos para acertos",
                "quantidade_de_relatorios": 0,
                "status": "DEVOLVIDO"
            },
            {
                "titulo": "Relatórios analisados",
                "quantidade_de_relatorios": 0,
                "status": "ANALISADO"
            }
        ],
        "total_de_relatorios": 1,
    }

    assert acompanhamento_dashboard == resultado_esperado


def test_acompanhamento_de_relatorios_consolidados_dashboard_1_publicado(
    periodo_teste_service_consolidado_dre,
    consolidado_dre_acompanhamento_de_relatorios_consolidados_dashboard_publicado

):
    acompanhamento_dashboard = Dashboard(periodo_teste_service_consolidado_dre).retorna_dashboard()

    resultado_esperado = {
        "cards": [
            {
                "titulo": "DREs sem relatório gerado",
                "quantidade_de_relatorios": 0,
                "status": "NAO_GERADO"
            },
            {
                "titulo": "Relatórios não publicados",
                "quantidade_de_relatorios": 0,
                "status": "NAO_PUBLICADO"
            },
            {
                "titulo": "Relatórios publicados",
                "quantidade_de_relatorios": 1,
                "status": "PUBLICADO"
            },
            {
                "titulo": "Relatórios em análise",
                "quantidade_de_relatorios": 0,
                "status": "EM_ANALISE"
            },
            {
                "titulo": "Relatórios devolvidos para acertos",
                "quantidade_de_relatorios": 0,
                "status": "DEVOLVIDO"
            },
            {
                "titulo": "Relatórios analisados",
                "quantidade_de_relatorios": 0,
                "status": "ANALISADO"
            }
        ],
        "total_de_relatorios": 1,
    }

    assert acompanhamento_dashboard == resultado_esperado


def test_acompanhamento_de_relatorios_consolidados_dashboard_1_nao_publicado_e_1_publicado(
    periodo_teste_service_consolidado_dre,
    consolidado_dre_acompanhamento_de_relatorios_consolidados_dashboard_publicado,
    consolidado_dre_acompanhamento_de_relatorios_consolidados_dashboard_nao_publicado

):
    acompanhamento_dashboard = Dashboard(periodo_teste_service_consolidado_dre).retorna_dashboard()

    resultado_esperado = {
        "cards": [
            {
                "titulo": "DREs sem relatório gerado",
                "quantidade_de_relatorios": 0,
                "status": "NAO_GERADO"
            },
            {
                "titulo": "Relatórios não publicados",
                "quantidade_de_relatorios": 1,
                "status": "NAO_PUBLICADO"
            },
            {
                "titulo": "Relatórios publicados",
                "quantidade_de_relatorios": 1,
                "status": "PUBLICADO"
            },
            {
                "titulo": "Relatórios em análise",
                "quantidade_de_relatorios": 0,
                "status": "EM_ANALISE"
            },
            {
                "titulo": "Relatórios devolvidos para acertos",
                "quantidade_de_relatorios": 0,
                "status": "DEVOLVIDO"
            },
            {
                "titulo": "Relatórios analisados",
                "quantidade_de_relatorios": 0,
                "status": "ANALISADO"
            }
        ],
        "total_de_relatorios": 2,
    }

    assert acompanhamento_dashboard == resultado_esperado


def test_acompanhamento_de_relatorios_consolidados_dashboard_1_nao_publicado_e_1_publicado_e_1_dre_sem_consolidado(
    periodo_teste_service_consolidado_dre,
    consolidado_dre_acompanhamento_de_relatorios_consolidados_dashboard_publicado,
    consolidado_dre_acompanhamento_de_relatorios_consolidados_dashboard_nao_publicado,
    dre_acompanhamento_de_relatorios_consolidados_dashboard_sem_consolidado_dre

):
    acompanhamento_dashboard = Dashboard(periodo_teste_service_consolidado_dre).retorna_dashboard()

    resultado_esperado = {
        "cards": [
            {
                "titulo": "DREs sem relatório gerado",
                "quantidade_de_relatorios": 1,
                "status": "NAO_GERADO"
            },
            {
                "titulo": "Relatórios não publicados",
                "quantidade_de_relatorios": 1,
                "status": "NAO_PUBLICADO"
            },
            {
                "titulo": "Relatórios publicados",
                "quantidade_de_relatorios": 1,
                "status": "PUBLICADO"
            },
            {
                "titulo": "Relatórios em análise",
                "quantidade_de_relatorios": 0,
                "status": "EM_ANALISE"
            },
            {
                "titulo": "Relatórios devolvidos para acertos",
                "quantidade_de_relatorios": 0,
                "status": "DEVOLVIDO"
            },
            {
                "titulo": "Relatórios analisados",
                "quantidade_de_relatorios": 0,
                "status": "ANALISADO"
            }
        ],
        "total_de_relatorios": 2,
    }

    assert acompanhamento_dashboard == resultado_esperado


def test_acompanhamento_de_relatorios_consolidados_dashboard_varias_dres(
    periodo_teste_service_consolidado_dre,
    consolidado_dre_acompanhamento_de_relatorios_consolidados_dashboard_publicado,
    consolidado_dre_acompanhamento_de_relatorios_consolidados_dashboard_nao_publicado,
    dre_acompanhamento_de_relatorios_consolidados_dashboard_sem_consolidado_dre,
    consolidado_dre_acompanhamento_de_relatorios_consolidados_dashboard_publicado_outra_dre,
    dre_acompanhamento_de_relatorios_consolidados_dashboard_com_consolidado_dre

):
    acompanhamento_dashboard = Dashboard(periodo_teste_service_consolidado_dre).retorna_dashboard()

    resultado_esperado = {
        "cards": [
            {
                "titulo": "DREs sem relatório gerado",
                "quantidade_de_relatorios": 1,
                "status": "NAO_GERADO"
            },
            {
                "titulo": "Relatórios não publicados",
                "quantidade_de_relatorios": 1,
                "status": "NAO_PUBLICADO"
            },
            {
                "titulo": "Relatórios publicados",
                "quantidade_de_relatorios": 2,
                "status": "PUBLICADO"
            },
            {
                "titulo": "Relatórios em análise",
                "quantidade_de_relatorios": 0,
                "status": "EM_ANALISE"
            },
            {
                "titulo": "Relatórios devolvidos para acertos",
                "quantidade_de_relatorios": 0,
                "status": "DEVOLVIDO"
            },
            {
                "titulo": "Relatórios analisados",
                "quantidade_de_relatorios": 0,
                "status": "ANALISADO"
            }
        ],
        "total_de_relatorios": 3,
    }

    assert acompanhamento_dashboard == resultado_esperado
