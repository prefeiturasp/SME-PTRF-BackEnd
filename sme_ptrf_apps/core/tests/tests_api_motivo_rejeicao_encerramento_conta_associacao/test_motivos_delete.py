import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import MotivoRejeicaoEncerramentoContaAssociacao

pytestmark = pytest.mark.django_db

def test_delete_motivo(
    jwt_authenticated_client_a,
    motivo_rejeicao
):
    assert MotivoRejeicaoEncerramentoContaAssociacao.objects.filter(uuid=motivo_rejeicao.uuid).exists()

    response = jwt_authenticated_client_a.delete(f'/api/motivos-rejeicao-encerramento-conta/{motivo_rejeicao.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not MotivoRejeicaoEncerramentoContaAssociacao.objects.filter(uuid=motivo_rejeicao.uuid).exists()
