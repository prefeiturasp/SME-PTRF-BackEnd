import json

import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import CobrancaPrestacaoConta

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_cobranca(prestacao_conta_2020_1_conciliada):
    payload = {
        'prestacao_conta': f'{prestacao_conta_2020_1_conciliada.uuid}',
        'data': "2020-10-10",
        'tipo': 'RECEBIMENTO'
    }
    return payload


def test_create_cobranca_prestacao_conta(jwt_authenticated_client_a, associacao, payload_cobranca,
                                         devolucao_prestacao_conta_2020_1):
    response = jwt_authenticated_client_a.post(
        '/api/cobrancas-prestacoes-contas/', data=json.dumps(payload_cobranca), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert CobrancaPrestacaoConta.objects.filter(uuid=result['uuid']).exists()

    cobranca = CobrancaPrestacaoConta.by_uuid(result['uuid'])

    assert cobranca.devolucao_prestacao is None, 'A cobrança não deveria estar vinculada à uma devolução da PC.'


@pytest.fixture
def payload_cobranca_sem_pc(associacao, periodo):
    payload = {
        'associacao': f'{associacao.uuid}',
        'periodo': f'{periodo.uuid}',
        'data': "2020-10-10",
        'tipo': 'RECEBIMENTO'
    }
    return payload


def test_create_cobranca_prestacao_conta_recebimento_sem_pc(jwt_authenticated_client_a, associacao, payload_cobranca_sem_pc,
                                                            devolucao_prestacao_conta_2020_1, periodo):
    response = jwt_authenticated_client_a.post(
        '/api/cobrancas-prestacoes-contas/', data=json.dumps(payload_cobranca_sem_pc), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert CobrancaPrestacaoConta.objects.filter(uuid=result['uuid']).exists()

    cobranca = CobrancaPrestacaoConta.by_uuid(result['uuid'])

    assert cobranca.associacao == associacao, 'A associacao não foi gravada.'
    assert cobranca.periodo == periodo, 'O período não foi gravado.'


@pytest.fixture
def payload_cobranca_devolucao(prestacao_conta_2020_1_conciliada):
    payload = {
        'prestacao_conta': f'{prestacao_conta_2020_1_conciliada.uuid}',
        'data': "2020-10-10",
        'tipo': 'DEVOLUCAO'
    }
    return payload


def test_create_cobranca_prestacao_conta_devolucao(jwt_authenticated_client_a, associacao, payload_cobranca_devolucao,
                                                   prestacao_conta_2020_1_conciliada,
                                                   devolucao_prestacao_conta_2020_1):
    response = jwt_authenticated_client_a.post(
        '/api/cobrancas-prestacoes-contas/', data=json.dumps(payload_cobranca_devolucao),
        content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert CobrancaPrestacaoConta.objects.filter(uuid=result['uuid']).exists(), 'Não criou a cobrança.'

    cobranca = CobrancaPrestacaoConta.by_uuid(result['uuid'])

    assert cobranca.devolucao_prestacao == devolucao_prestacao_conta_2020_1, 'A cobrança não foi vinculada à ultima devolução da PC.'
