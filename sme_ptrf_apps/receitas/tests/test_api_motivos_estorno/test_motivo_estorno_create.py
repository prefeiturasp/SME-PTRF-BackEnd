import json
import pytest
from rest_framework import status
from sme_ptrf_apps.receitas.models import MotivoEstorno

pytestmark = pytest.mark.django_db


def test_create_motivo_estorno(jwt_authenticated_client_p, recurso_legado):
    payload = {
        'motivo': 'Motivo teste',
        'recurso': str(recurso_legado.uuid)
    }

    response = jwt_authenticated_client_p.post(
        f'/api/motivos-estorno/', data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert MotivoEstorno.objects.filter(uuid=result['uuid']).exists()

