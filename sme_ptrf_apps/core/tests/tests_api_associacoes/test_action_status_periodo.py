import json
import pytest

from datetime import date

from freezegun import freeze_time
from model_bakery import baker
from rest_framework import status

from ...models import PrestacaoConta, Periodo

pytestmark = pytest.mark.django_db


@freeze_time('2020-01-10 10:11:12')
def test_status_periodo_em_andamento(jwt_authenticated_client_a, associacao, periodo_fim_em_aberto):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data=2020-01-10',
                          content_type='application/json')
    result = json.loads(response.content)
    esperado = {
        'associacao': f'{associacao.uuid}',
        'gerar_ou_editar_ata_apresentacao': True,
        'gerar_ou_editar_ata_retificacao': False,
        'gerar_previas': True,
        'periodo_referencia': periodo_fim_em_aberto.referencia,
        'aceita_alteracoes': True,
        'prestacao_contas_status': {
            'documentos_gerados': False,
            'pc_requer_conclusao': True,
            'legenda_cor': 1,
            'periodo_bloqueado': False,
            'periodo_encerrado': None,
            'status_prestacao': 'NAO_APRESENTADA',
            'texto_status': 'Período em andamento. ',
            'prestacao_de_contas_uuid': None,
            'requer_retificacao': False,
            'tem_acertos_pendentes': False,
        },
        'prestacao_conta': '',
        'pendencias_cadastrais': {
            'conciliacao_bancaria': None,
            'dados_associacao': {
                'pendencia_cadastro': False,
                'pendencia_contas': False,
                'pendencia_membros': True
            }
        }
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


@freeze_time('2020-07-10 10:20:00')
def test_status_periodo_pendente(jwt_authenticated_client_a, associacao, periodo_fim_em_2020_06_30):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data=2020-01-10',
                          content_type='application/json')
    result = json.loads(response.content)
    esperado = {
        'associacao': f'{associacao.uuid}',
        'gerar_ou_editar_ata_apresentacao': True,
        'gerar_ou_editar_ata_retificacao': False,
        'gerar_previas': True,
        'periodo_referencia': periodo_fim_em_2020_06_30.referencia,
        'aceita_alteracoes': True,
        'prestacao_contas_status': {
            'documentos_gerados': False,
            'pc_requer_conclusao': True,
            'legenda_cor': 3,
            'periodo_bloqueado': False,
            'periodo_encerrado': True,
            'status_prestacao': 'NAO_APRESENTADA',
            'texto_status': 'Período finalizado. Documentos pendentes de geração.',
            'prestacao_de_contas_uuid': None,
            'requer_retificacao': False,
            'tem_acertos_pendentes': False,
        },
        'prestacao_conta': '',
        'pendencias_cadastrais': {
            'conciliacao_bancaria': None,
            'dados_associacao': {
                'pendencia_cadastro': False,
                'pendencia_contas': False,
                'pendencia_membros': True
            }
        }

    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_chamada_sem_passar_data(jwt_authenticated_client_a, associacao, periodo_2020_1, prestacao_conta_2020_1_conciliada):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/status-periodo/',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'erro': 'parametros_requerido',
        'mensagem': 'É necessário enviar a data que você quer consultar o status.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado


def test_chamada_data_sem_periodo(jwt_authenticated_client_a, associacao, periodo_2020_1):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data=2000-01-10',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'gerar_ou_editar_ata_apresentacao': False,
        'gerar_ou_editar_ata_retificacao': False,
        'gerar_previas': True,
        'periodo_referencia': '',
        'aceita_alteracoes': True,
        'prestacao_contas_status': {},
        'prestacao_conta': '',
        'pendencias_cadastrais': {
            'conciliacao_bancaria': None,
            'dados_associacao': {
                'pendencia_cadastro': False,
                'pendencia_contas': False,
                'pendencia_membros': True
            }
        }
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


@freeze_time('2020-07-10 10:20:00')
def test_status_periodo_finalizado(jwt_authenticated_client_a, associacao, prestacao_conta_2020_1_conciliada):
    periodo = prestacao_conta_2020_1_conciliada.periodo

    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data={periodo.data_inicio_realizacao_despesas}',
                          content_type='application/json')
    result = json.loads(response.content)
    esperado = {
        'associacao': f'{associacao.uuid}',
        'gerar_ou_editar_ata_apresentacao': True,
        'gerar_ou_editar_ata_retificacao': False,
        'gerar_previas': False,
        'periodo_referencia': periodo.referencia,
        'aceita_alteracoes': False,
        'prestacao_contas_status': {
            'documentos_gerados': True,
            'pc_requer_conclusao': False,
            'legenda_cor': 2,
            'periodo_bloqueado': True,
            'periodo_encerrado': True,
            'status_prestacao': 'NAO_RECEBIDA',
            'texto_status': 'Período finalizado. Prestação de contas ainda não recebida pela DRE.',
            'prestacao_de_contas_uuid': f'{prestacao_conta_2020_1_conciliada.uuid}',
            'requer_retificacao': False,
            'tem_acertos_pendentes': False,
        },
        'prestacao_conta': f'{prestacao_conta_2020_1_conciliada.uuid}',
        'pendencias_cadastrais': {
            'conciliacao_bancaria': None,
            'dados_associacao': {
                'pendencia_cadastro': False,
                'pendencia_contas': False,
                'pendencia_membros': True
            }
        }

    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado



@pytest.fixture
def _prestacao_conta_devolvida(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        data_ultima_analise=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_DEVOLVIDA
    )


@freeze_time('2020-07-10 10:20:00')
def test_status_periodo_devolvido_para_acertos(jwt_authenticated_client_a, associacao, _prestacao_conta_devolvida):
    periodo = _prestacao_conta_devolvida.periodo

    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data={periodo.data_inicio_realizacao_despesas}',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'gerar_ou_editar_ata_apresentacao': False,
        'gerar_ou_editar_ata_retificacao': True,
        'gerar_previas': False,
        'periodo_referencia': periodo.referencia,
        'aceita_alteracoes': False,
        'prestacao_contas_status': {
            'documentos_gerados': True,
            'pc_requer_conclusao': True,
            'legenda_cor': 3,
            'periodo_bloqueado': True,
            'periodo_encerrado': True,
            'status_prestacao': 'DEVOLVIDA',
            'texto_status': 'Período finalizado. Prestação de contas devolvida para ajustes.',
            'prestacao_de_contas_uuid': f'{_prestacao_conta_devolvida.uuid}',
            'requer_retificacao': False,
            'tem_acertos_pendentes': False,
        },
        'prestacao_conta': f'{_prestacao_conta_devolvida.uuid}',
        'pendencias_cadastrais': {
            'conciliacao_bancaria': None,
            'dados_associacao': {
                'pendencia_cadastro': False,
                'pendencia_contas': False,
                'pendencia_membros': True
            }
        }

    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado

@freeze_time('2020-07-10 10:20:00')
def test_status_periodo_pendencias_cadastrais_com_contas_pendentes(
    jwt_authenticated_client_a, associacao,
    observacao_conciliacao_campos_nao_preenchidos,
    observacao_conciliacao_campos_nao_preenchidos_002,
    periodo_2020_1
):

    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data={periodo_2020_1.data_inicio_realizacao_despesas}',
                          content_type='application/json')
    result = json.loads(response.content)

    pendencias_cadastrais_esperado = {
        'conciliacao_bancaria': {
            'contas_pendentes': [f'{observacao_conciliacao_campos_nao_preenchidos.conta_associacao.uuid}', f'{observacao_conciliacao_campos_nao_preenchidos_002.conta_associacao.uuid}',],
        },
        'dados_associacao': {
            'pendencia_cadastro': False,
            'pendencia_contas': False,
            'pendencia_membros': True
        }
    }

    assert response.status_code == status.HTTP_200_OK
    assert result['pendencias_cadastrais'] == pendencias_cadastrais_esperado

@freeze_time('2020-07-10 10:20:00')
def test_status_periodo_pendencias_cadastrais_somente_uma_conta_pendente(
    jwt_authenticated_client_a, associacao,
    observacao_conciliacao_campos_nao_preenchidos_002,
    observacao_conciliacao_com_saldo_zero,
    periodo_2020_1
):

    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data={periodo_2020_1.data_inicio_realizacao_despesas}',
                          content_type='application/json')
    result = json.loads(response.content)

    pendencias_cadastrais_esperado = {
        'conciliacao_bancaria': {
            'contas_pendentes': [f'{observacao_conciliacao_campos_nao_preenchidos_002.conta_associacao.uuid}',],
        },
        'dados_associacao': {
            'pendencia_cadastro': False,
            'pendencia_contas': False,
            'pendencia_membros': True
        }
    }

    assert response.status_code == status.HTTP_200_OK
    assert result['pendencias_cadastrais'] == pendencias_cadastrais_esperado

@freeze_time('2020-07-10 10:20:00')
def test_status_periodo_pendencias_cadastrais_sem_contas_pendentes(
    jwt_authenticated_client_a,
    associacao,
    periodo_2020_1,
):

    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data={periodo_2020_1.data_inicio_realizacao_despesas}',
                          content_type='application/json')
    result = json.loads(response.content)

    pendencias_cadastrais_esperado = {
        'conciliacao_bancaria': None,
        'dados_associacao': {
            'pendencia_cadastro': False,
            'pendencia_contas': False,
            'pendencia_membros': True
        }
    }

    assert response.status_code == status.HTTP_200_OK
    assert result['pendencias_cadastrais'] == pendencias_cadastrais_esperado

@freeze_time('2020-07-10 10:20:00')
def test_status_periodo_pendencias_cadastrais_somente_dados_associacao_com_pendencia_cadastro_e_pendencia_membros(
    jwt_authenticated_client_a,
    associacao_cadastro_incompleto,
    periodo_2020_1,
):

    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao_cadastro_incompleto.uuid}/status-periodo/?data={periodo_2020_1.data_inicio_realizacao_despesas}',
                          content_type='application/json')
    result = json.loads(response.content)

    pendencias_cadastrais_esperado = {
        'conciliacao_bancaria': None,
        'dados_associacao': {
            'pendencia_cadastro': True,
            'pendencia_contas': False,
            'pendencia_membros': True
        }
    }

    assert response.status_code == status.HTTP_200_OK
    assert result['pendencias_cadastrais'] == pendencias_cadastrais_esperado

@freeze_time('2020-07-10 10:20:00')
def test_status_periodo_todas_as_pendencias_cadastrais(
    jwt_authenticated_client_a,
    conta_associacao_incompleta,
    periodo_2020_1,
):

    response = jwt_authenticated_client_a.get(f'/api/associacoes/{conta_associacao_incompleta.associacao.uuid}/status-periodo/?data={periodo_2020_1.data_inicio_realizacao_despesas}',
                          content_type='application/json')
    result = json.loads(response.content)

    pendencias_cadastrais_esperado = {
        'dados_associacao': {
            'pendencia_cadastro': True,
            'pendencia_membros': True,
            'pendencia_contas': True,
        },
        'conciliacao_bancaria': {
            'contas_pendentes': [f'{conta_associacao_incompleta.uuid}']
        },
    }

    assert response.status_code == status.HTTP_200_OK
    assert result['pendencias_cadastrais'] == pendencias_cadastrais_esperado
