import json
import pytest
from rest_framework import status
from sme_ptrf_apps.despesas.models import TipoCusteio

pytestmark = pytest.mark.django_db


def test_update_tipo_custeio(jwt_authenticated_client_d, tipo_custeio_01, payload_update_tag):

    assert TipoCusteio.objects.get(uuid=tipo_custeio_01.uuid).nome == 'Servico 01'

    response = jwt_authenticated_client_d.patch(
        f'/api/tipos-custeio/{tipo_custeio_01.uuid}/',
        data=json.dumps(payload_update_tag),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK

    assert TipoCusteio.objects.get(uuid=tipo_custeio_01.uuid).nome == payload_update_tag['nome']
