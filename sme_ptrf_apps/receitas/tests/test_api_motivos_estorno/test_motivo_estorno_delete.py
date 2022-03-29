import json
import pytest
from rest_framework import status
from sme_ptrf_apps.receitas.models import MotivoEstorno

pytestmark = pytest.mark.django_db


def test_delete_motivo_estorno(jwt_authenticated_client_p, motivo_estorno_01):
    assert MotivoEstorno.objects.filter(uuid=motivo_estorno_01.uuid).exists()

    response = jwt_authenticated_client_p.delete(
        f'/api/motivos-estorno/{motivo_estorno_01.uuid}/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not MotivoEstorno.objects.filter(uuid=motivo_estorno_01.uuid).exists()

