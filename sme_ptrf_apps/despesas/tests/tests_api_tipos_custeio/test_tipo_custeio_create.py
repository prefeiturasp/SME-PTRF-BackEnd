import json
import pytest
from rest_framework import status
from sme_ptrf_apps.despesas.models import TipoCusteio

pytestmark = pytest.mark.django_db


def test_create_tipo_custeio(jwt_authenticated_client_d):

    payload_novo_tipo_custeio = {
        'nome': 'Tipo de Custeio Novo',
    }

    response = jwt_authenticated_client_d.post(
        f'/api/tipos-custeio/', data=json.dumps(payload_novo_tipo_custeio),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert TipoCusteio.objects.filter(uuid=result['uuid']).exists()
