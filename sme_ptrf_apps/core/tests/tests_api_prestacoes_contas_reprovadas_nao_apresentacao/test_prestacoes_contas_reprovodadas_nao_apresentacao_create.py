import json
from datetime import datetime

import pytest
from rest_framework import status
from waffle.testutils import override_flag

pytestmark = pytest.mark.django_db


@override_flag('pc-reprovada-nao-apresentacao', active=True)
def test_create(jwt_authenticated_client_a, periodo_factory, associacao_factory):
    data_de_reprovacao = datetime(2024, 3, 4)

    payload = {
        "periodo": f"{periodo_factory.create().uuid}",
        "associacao": f"{associacao_factory.create().uuid}",
        "data_de_reprovacao": f"{data_de_reprovacao}"
    }
    response = jwt_authenticated_client_a.post(
        f'/api/prestacoes-contas-reprovadas-nao-apresentacao/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_201_CREATED
