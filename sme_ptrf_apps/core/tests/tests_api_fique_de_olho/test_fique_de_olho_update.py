import json
import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import FiqueDeOlho

pytestmark = pytest.mark.django_db


def test_update_fique_de_olho(jwt_authenticated_client_a, fique_de_olho_a, payload_update_fique_de_olho):

    assert FiqueDeOlho.objects.get(uuid=fique_de_olho_a.uuid).texto == 'Texto do Fique de Olho A'

    response = jwt_authenticated_client_a.patch(
        f'/api/fique-de-olho/{fique_de_olho_a.uuid}/',
        data=json.dumps(payload_update_fique_de_olho),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK

    assert FiqueDeOlho.objects.get(uuid=fique_de_olho_a.uuid).texto == payload_update_fique_de_olho['texto']
