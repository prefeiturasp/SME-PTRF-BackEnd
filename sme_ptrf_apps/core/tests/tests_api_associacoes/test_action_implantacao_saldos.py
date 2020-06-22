import json

import pytest
from freezegun import freeze_time
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_implanta_saldos_saldos_ainda_nao_implantados(client, associacao, periodo_anterior):
    response = client.get(f'/api/associacoes/{associacao.uuid}/implantacao-saldos/',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo': {
            'referencia': '2019.1',
            'data_inicio_realizacao_despesas': '2019-01-01',
            'data_fim_realizacao_despesas': '2019-08-31',
            'uuid': f'{periodo_anterior.uuid}'
        },
        'saldos': [],
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_retrieve_implanta_saldos_saldos_ja_implantados(client, associacao, periodo_anterior,
                                                        fechamento_periodo_anterior_role_implantado,
                                                        acao_associacao_role_cultural,
                                                        conta_associacao):
    response = client.get(f'/api/associacoes/{associacao.uuid}/implantacao-saldos/',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo': {
            'referencia': '2019.1',
            'data_inicio_realizacao_despesas': '2019-01-01',
            'data_fim_realizacao_despesas': '2019-08-31',
            'uuid': f'{periodo_anterior.uuid}'
        },
        'saldos': [
            {
                'acao_associacao': {
                    'id': acao_associacao_role_cultural.id,
                    'uuid': f'{acao_associacao_role_cultural.uuid}',
                    'nome': acao_associacao_role_cultural.acao.nome
                },
                'conta_associacao': {
                    'uuid': f'{conta_associacao.uuid}',
                    'nome': f'{conta_associacao.tipo_conta.nome}'
                },
                'aplicacao': 'CAPITAL',
                'saldo': 1000.0
            },
            {
                'acao_associacao': {
                    'id': acao_associacao_role_cultural.id,
                    'uuid': f'{acao_associacao_role_cultural.uuid}',
                    'nome': acao_associacao_role_cultural.acao.nome
                },
                'conta_associacao': {
                    'uuid': f'{conta_associacao.uuid}',
                    'nome': f'{conta_associacao.tipo_conta.nome}'
                },
                'aplicacao': 'CUSTEIO',
                'saldo': 2000.0
            }
        ],
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


@freeze_time('2020-07-10 10:20:00')
def test_retrieve_implanta_saldos_sem_periodo_inicial_definido(client, associacao_sem_periodo_inicial,
                                                               periodo_anterior):
    response = client.get(f'/api/associacoes/{associacao_sem_periodo_inicial.uuid}/implantacao-saldos/',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'erro': 'periodo_inicial_nao_definido',
        'mensagem': 'Período inicial não foi definido para essa associação. Verifique com o administrador.'
    }

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert result == esperado


def test_retrieve_implanta_saldos_com_prestacao_contas(client, associacao, periodo_anterior, prestacao_conta_iniciada):
    response = client.get(f'/api/associacoes/{associacao.uuid}/implantacao-saldos/',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'erro': 'prestacao_de_contas_existente',
        'mensagem': 'Os saldos não podem ser implantados, já existe uma prestação de contas da associação.'
    }

    assert response.status_code == status.HTTP_409_CONFLICT
    assert result == esperado
