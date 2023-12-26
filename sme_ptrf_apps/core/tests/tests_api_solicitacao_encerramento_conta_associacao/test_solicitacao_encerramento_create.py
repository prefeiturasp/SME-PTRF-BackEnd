import json
import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import SolicitacaoEncerramentoContaAssociacao, ContaAssociacao
from sme_ptrf_apps.despesas.models import RateioDespesa
pytestmark = pytest.mark.django_db

def test_create_solicitacao_encerramento_conta_associacao(jwt_authenticated_client_a, associacao, payload_valido_solicitacao_encerramento):
    response = jwt_authenticated_client_a.post(
        '/api/solicitacoes-encerramento-conta/', data=json.dumps(payload_valido_solicitacao_encerramento), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert SolicitacaoEncerramentoContaAssociacao.objects.filter(uuid=result['uuid']).exists()

def test_status_conta_associacao_apos_create_solicitacao_encerramento(
        jwt_authenticated_client_a,
        associacao,
        conta_associacao,
        payload_valido_solicitacao_encerramento
    ):
    response = jwt_authenticated_client_a.post(
        '/api/solicitacoes-encerramento-conta/', data=json.dumps(payload_valido_solicitacao_encerramento), content_type='application/json')

    solicitacao = SolicitacaoEncerramentoContaAssociacao.objects.get(uuid=response.data['uuid'])

    assert response.status_code == status.HTTP_201_CREATED

    assert solicitacao.conta_associacao.status == ContaAssociacao.STATUS_INATIVA

def test_validacao_saldo_da_conta_maior_que_zero_create_solicitacao_encerramento(
        jwt_authenticated_client_a,
        associacao,
        conta_associacao,
        receita_no_periodo,
        despesa_no_periodo,
        payload_valido_solicitacao_encerramento
    ):
    response = jwt_authenticated_client_a.post(
        '/api/solicitacoes-encerramento-conta/', data=json.dumps(payload_valido_solicitacao_encerramento), content_type='application/json')

    assert response.json()['mensagem']

    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_validacao_movimentacoes_apos_data_encerramento_create_solicitacao_encerramento(
        jwt_authenticated_client_a,
        associacao,
        conta_associacao,
        despesa_no_periodo,
        rateio_despesa_demonstrativo,
        payload_valido_solicitacao_encerramento
    ):

    response = jwt_authenticated_client_a.post(
        '/api/solicitacoes-encerramento-conta/', data=json.dumps(payload_valido_solicitacao_encerramento), content_type='application/json')

    assert response.json()['mensagem']

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_validacao_periodo_inicial_create_solicitacao_encerramento(
        jwt_authenticated_client_a,
        associacao,
        conta_associacao,
        payload_solicitacao_encerramento_data_invalida
    ):
    response = jwt_authenticated_client_a.post(
        '/api/solicitacoes-encerramento-conta/', data=json.dumps(payload_solicitacao_encerramento_data_invalida), content_type='application/json')
    assert response.json()['mensagem']

    assert response.status_code == status.HTTP_400_BAD_REQUEST
