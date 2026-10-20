import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import FiqueDeOlho

pytestmark = pytest.mark.django_db


def test_fique_de_olho_delete(jwt_authenticated_client_a, fique_de_olho_a):
    assert FiqueDeOlho.objects.filter(uuid=fique_de_olho_a.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/fique-de-olho/{fique_de_olho_a.uuid}/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
