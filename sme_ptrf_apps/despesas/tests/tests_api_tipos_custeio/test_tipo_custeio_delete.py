import pytest
from rest_framework import status
from sme_ptrf_apps.despesas.models import TipoCusteio

pytestmark = pytest.mark.django_db


def test_delete_tipo_custeio(jwt_authenticated_client_d, tipo_custeio_01):
    assert TipoCusteio.objects.filter(uuid=tipo_custeio_01.uuid).exists()

    response = jwt_authenticated_client_d.delete(
        f'/api/tipos-custeio/{tipo_custeio_01.uuid}/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not TipoCusteio.objects.filter(uuid=tipo_custeio_01.uuid).exists()
