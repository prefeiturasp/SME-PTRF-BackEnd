import json
import pytest

from rest_framework import status
from sme_ptrf_apps.core.models import MotivoRejeicaoEncerramentoContaAssociacao

pytestmark = pytest.mark.django_db

def test_update_motivo(
    jwt_authenticated_client_a,
    motivo_rejeicao,
    payload_update_motivo_rejeicao_valido
):
    response = jwt_authenticated_client_a.put(
        f'/api/motivos-rejeicao-encerramento-conta/{motivo_rejeicao.uuid}/',
        data=json.dumps(payload_update_motivo_rejeicao_valido),
        content_type='application/json')

    result = json.loads(response.content)

    motivo = MotivoRejeicaoEncerramentoContaAssociacao.objects.get(uuid=motivo_rejeicao.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert result['nome'] == 'Pix da conta inválido'
    assert motivo.nome == 'Pix da conta inválido'
