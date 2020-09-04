import json

import pytest
from freezegun import freeze_time
from rest_framework import status

from ...status_periodo_associacao import (STATUS_PERIODO_ASSOCIACAO_EM_ANDAMENTO, STATUS_PERIODO_ASSOCIACAO_PENDENTE)

pytestmark = pytest.mark.django_db


@freeze_time('2020-01-10 10:11:12')
def test_status_periodo_em_andamento(client, associacao, periodo_fim_em_aberto):
    response = client.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data=2020-01-10',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo_referencia': periodo_fim_em_aberto.referencia,
        'periodo_status': STATUS_PERIODO_ASSOCIACAO_EM_ANDAMENTO,
        'aceita_alteracoes': True,
        'prestacao_contas_status': {
            'documentos_gerados': None,
            'legenda_cor': 1,
            'periodo_bloqueado': False,
            'periodo_encerrado': None,
            'status_prestacao': 'DOCS_PENDENTES',
            'texto_status': 'Período em andamento. '
        }

    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


@freeze_time('2020-07-10 10:20:00')
def test_status_periodo_pendente(client, associacao, periodo_fim_em_2020_06_30):
    response = client.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data=2020-01-10',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo_referencia': periodo_fim_em_2020_06_30.referencia,
        'periodo_status': STATUS_PERIODO_ASSOCIACAO_PENDENTE,
        'aceita_alteracoes': True,
        'prestacao_contas_status': {
            'documentos_gerados': None,
            'legenda_cor': 3,
            'periodo_bloqueado': False,
            'periodo_encerrado': True,
            'status_prestacao': 'DOCS_PENDENTES',
            'texto_status': 'Período finalizado. Documentos pendentes de geração.'
        }

    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_chamada_sem_passar_data(client, associacao, periodo_2020_1, prestacao_conta_2020_1_conciliada):
    response = client.get(f'/api/associacoes/{associacao.uuid}/status-periodo/',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'erro': 'parametros_requerido',
        'mensagem': 'É necessário enviar a data que você quer consultar o status.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado


def test_chamada_data_sem_periodo(client, associacao, periodo_2020_1):
    response = client.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data=2000-01-10',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo_referencia': '',
        'periodo_status': 'PERIODO_NAO_ENCONTRADO',
        'aceita_alteracoes': True,
        'prestacao_contas_status': {}
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
