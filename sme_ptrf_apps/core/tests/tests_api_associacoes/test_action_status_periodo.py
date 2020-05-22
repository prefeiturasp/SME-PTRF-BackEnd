import json

import pytest
from freezegun import freeze_time
from rest_framework import status

from ...status_periodo_associacao import (STATUS_PERIODO_ASSOCIACAO_EM_ANDAMENTO, STATUS_PERIODO_ASSOCIACAO_PENDENTE,
                                          STATUS_PERIODO_ASSOCIACAO_CONCILIADO)

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

    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_status_periodo_conciliado(client, associacao, periodo_2020_1, prestacao_conta_2020_1_conciliada):
    response = client.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data=2020-01-10',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo_referencia': periodo_2020_1.referencia,
        'periodo_status': STATUS_PERIODO_ASSOCIACAO_CONCILIADO,
        'aceita_alteracoes': False,

    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
