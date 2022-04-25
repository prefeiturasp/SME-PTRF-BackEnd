import json
import pytest
from rest_framework import status
from sme_ptrf_apps.receitas.models import MotivoEstorno

pytestmark = pytest.mark.django_db


def test_update_motivo_estorno(jwt_authenticated_client_p, motivo_estorno_01):
    assert MotivoEstorno.objects.get(uuid=motivo_estorno_01.uuid).motivo == 'Motivo de estorno 01'

    payload = {
        'motivo': 'Motivo de estorno 01 atualizado'
    }

    response = jwt_authenticated_client_p.patch(
        f'/api/motivos-estorno/{motivo_estorno_01.uuid}/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
    assert MotivoEstorno.objects.get(uuid=motivo_estorno_01.uuid).motivo == payload['motivo']

