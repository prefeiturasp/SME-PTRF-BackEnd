import pytest
from ...services.consolidado_dre_service import retornar_trilha_de_status

pytestmark = pytest.mark.django_db


def test_retorna_trilha_de_status_sem_nenhuma_pc(
    dre_teste_service_consolidado_dre,
    periodo_teste_service_consolidado_dre
):
    dre_uuid = dre_teste_service_consolidado_dre.uuid
    periodo_uuid = periodo_teste_service_consolidado_dre.uuid

    result = retornar_trilha_de_status(dre_uuid, periodo_uuid)
    resultado_esperado = [
        {
            'estilo_css': 2,
            'quantidade_nao_recebida': 0,
            'quantidade_prestacoes': 0,
            'status': 'NAO_RECEBIDA',
            'titulo': 'Não recebidas'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 0,
            'status': 'RECEBIDA',
            'titulo': 'Recebidas e<br/>aguardando análise'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 0,
            'status': 'DEVOLVIDA',
            'titulo': 'Devolvidas <br/>para acertos'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 0,
            'status': 'EM_ANALISE',
            'titulo': 'Em análise'
        },
        {
            'estilo_css': 1,
            'quantidade_prestacoes': 0,
            'status': 'CONCLUIDO',
            'titulo': 'Concluídas <br/>Documentos não gerados'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 0,
            'status': 'PUBLICADO',
            'titulo': 'Concluídas <br/>Documentos gerados'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 0,
            'status': 'APROVADA',
            'titulo': 'Aprovadas'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 0,
            'status': 'REPROVADA',
            'titulo': 'Reprovadas'
        }
    ]
    assert result == resultado_esperado


def test_retorna_trilha_de_status_uma_pc_aprovada_e_uma_concluida(
    dre_teste_service_consolidado_dre,
    periodo_teste_service_consolidado_dre,
    prestacao_conta_aprovada_teste_service
):
    dre_uuid = dre_teste_service_consolidado_dre.uuid
    periodo_uuid = periodo_teste_service_consolidado_dre.uuid

    result = retornar_trilha_de_status(dre_uuid, periodo_uuid)

    resultado_esperado = [
        {
            'estilo_css': 2,
            'quantidade_nao_recebida': 0,
            'quantidade_prestacoes': 0,
            'status': 'NAO_RECEBIDA',
            'titulo': 'Não recebidas'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 0,
            'status': 'RECEBIDA',
            'titulo': 'Recebidas e<br/>aguardando análise'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 0,
            'status': 'DEVOLVIDA',
            'titulo': 'Devolvidas <br/>para acertos'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 0,
            'status': 'EM_ANALISE',
            'titulo': 'Em análise'
        },
        {
            'estilo_css': 1,
            'quantidade_prestacoes': 1,
            'status': 'CONCLUIDO',
            'titulo': 'Concluídas <br/>Documentos não gerados'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 0,
            'status': 'PUBLICADO',
            'titulo': 'Concluídas <br/>Documentos gerados'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 1,
            'status': 'APROVADA',
            'titulo': 'Aprovadas'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 0,
            'status': 'REPROVADA',
            'titulo': 'Reprovadas'
        }
    ]

    assert result == resultado_esperado


def test_retorna_trilha_de_status_uma_pc_reprovada_uma_concluida_e_uma_publicada(
    dre_teste_service_consolidado_dre,
    periodo_teste_service_consolidado_dre,
    consolidado_dre_teste_service_consolidado_dre,
    prestacao_conta_aprovada_teste_service,
    prestacao_conta_reprovada_teste_service_publicada
):
    dre_uuid = dre_teste_service_consolidado_dre.uuid
    periodo_uuid = periodo_teste_service_consolidado_dre.uuid

    result = retornar_trilha_de_status(dre_uuid, periodo_uuid)

    resultado_esperado = [
        {
            'estilo_css': 2,
            'quantidade_nao_recebida': 0,
            'quantidade_prestacoes': 0,
            'status': 'NAO_RECEBIDA',
            'titulo': 'Não recebidas'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 0,
            'status': 'RECEBIDA',
            'titulo': 'Recebidas e<br/>aguardando análise'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 0,
            'status': 'DEVOLVIDA',
            'titulo': 'Devolvidas <br/>para acertos'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 0,
            'status': 'EM_ANALISE',
            'titulo': 'Em análise'
        },
        {
            'estilo_css': 1,
            'quantidade_prestacoes': 1,
            'status': 'CONCLUIDO',
            'titulo': 'Concluídas <br/>Documentos não gerados'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 1,
            'status': 'PUBLICADO',
            'titulo': 'Concluídas <br/>Documentos gerados'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 1,
            'status': 'APROVADA',
            'titulo': 'Aprovadas'
        },
        {
            'estilo_css': 0,
            'quantidade_prestacoes': 1,
            'status': 'REPROVADA',
            'titulo': 'Reprovadas'
        }
    ]
    assert result == resultado_esperado
