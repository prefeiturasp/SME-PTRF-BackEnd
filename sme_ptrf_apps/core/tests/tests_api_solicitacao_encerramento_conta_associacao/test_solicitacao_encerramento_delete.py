import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import ContaAssociacao
pytestmark = pytest.mark.django_db

def test_status_conta_associacao_apos_delete_solicitacao_encerramento(
        jwt_authenticated_client_a,
        solicitacao_encerramento
    ):
    response = jwt_authenticated_client_a.delete('/api/solicitacoes-encerramento-conta/' + str(solicitacao_encerramento.uuid) + '/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    conta_associacao = ContaAssociacao.objects.get(id=solicitacao_encerramento.conta_associacao.id)

    assert conta_associacao.status == ContaAssociacao.STATUS_ATIVA

def test_validacao_delete_solicitacao_encerramento_conta_associacao(
        jwt_authenticated_client_a,
        solicitacao_encerramento_aprovada
    ):
    response = jwt_authenticated_client_a.delete('/api/solicitacoes-encerramento-conta/' + str(solicitacao_encerramento_aprovada.uuid) + '/', content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
