import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import Arquivo

pytestmark = pytest.mark.django_db


def test_delete_arquivo(
    jwt_authenticated_client_a,
    arquivo_carga
):
    assert Arquivo.objects.filter(uuid=arquivo_carga.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/arquivos/{arquivo_carga.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Arquivo.objects.filter(uuid=arquivo_carga.uuid).exists()
