import pytest
from rest_framework import status

from sme_ptrf_apps.dre.models import TecnicoDre

pytestmark = pytest.mark.django_db

def test_delete_tecnico_dre(jwt_authenticated_client, tecnico_jose_dre_ipiranga):
    assert TecnicoDre.objects.filter(uuid=tecnico_jose_dre_ipiranga.uuid).exists()

    response = jwt_authenticated_client.delete(
        f'/api/tecnicos-dre/{tecnico_jose_dre_ipiranga.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not TecnicoDre.objects.filter(uuid=tecnico_jose_dre_ipiranga.uuid).exists()
