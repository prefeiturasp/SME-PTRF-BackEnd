import json
import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import SolicitacaoEncerramentoContaAssociacao, ContaAssociacao
pytestmark = pytest.mark.django_db

def test_reenviar_solicitacao_encerramento_conta_associacao(jwt_authenticated_client_a, solicitacao_encerramento_reprovada):
    response = jwt_authenticated_client_a.patch(
        f'/api/solicitacoes-encerramento-conta/{solicitacao_encerramento_reprovada.uuid}/reenviar/', content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

def test_validacao_reenviar_solicitacao_encerramento_conta_associacao(jwt_authenticated_client_a, solicitacao_encerramento):
    response = jwt_authenticated_client_a.patch(
        f'/api/solicitacoes-encerramento-conta/{solicitacao_encerramento.uuid}/reenviar/', content_type='application/json')

    assert response.json()['erro'] == 'status_nao_permite_operacao'
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_aprovar_solicitacao_encerramento_conta_associacao(jwt_authenticated_client_a, solicitacao_encerramento):
    response = jwt_authenticated_client_a.patch(
        f'/api/solicitacoes-encerramento-conta/{solicitacao_encerramento.uuid}/aprovar/', content_type='application/json')

    assert response.json()['status'] == SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA
    assert response.json()['data_aprovacao']
    assert response.status_code == status.HTTP_200_OK

def test_validacao_aprovar_solicitacao_encerramento_conta_associacao(jwt_authenticated_client_a, solicitacao_encerramento_reprovada):
    response = jwt_authenticated_client_a.patch(
        f'/api/solicitacoes-encerramento-conta/{solicitacao_encerramento_reprovada.uuid}/aprovar/', content_type='application/json')

    assert response.json()['erro'] == 'status_nao_permite_operacao'
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_rejeitar_solicitacao_encerramento_conta_associacao(jwt_authenticated_client_a, solicitacao_encerramento, payload_rejeitar_solicitacao):
    response = jwt_authenticated_client_a.patch(
        f'/api/solicitacoes-encerramento-conta/{solicitacao_encerramento.uuid}/rejeitar/',
        data=json.dumps(payload_rejeitar_solicitacao),
        content_type='application/json')

    assert response.json()['status'] == SolicitacaoEncerramentoContaAssociacao.STATUS_REJEITADA
    assert response.json()['motivos_rejeicao']
    assert response.json()['outros_motivos_rejeicao'] == 'UE com pendências cadastrais.'
    assert response.status_code == status.HTTP_200_OK

def test_validacao_rejeitar_solicitacao_encerramento_conta_associacao(jwt_authenticated_client_a, solicitacao_encerramento_reprovada):
    response = jwt_authenticated_client_a.patch(
        f'/api/solicitacoes-encerramento-conta/{solicitacao_encerramento_reprovada.uuid}/rejeitar/', content_type='application/json')

    assert response.json()['erro'] == 'status_nao_permite_operacao'
    assert response.status_code == status.HTTP_400_BAD_REQUEST
