import json

import pytest
from rest_framework import status


pytestmark = pytest.mark.django_db


def test_get_sucesso(jwt_authenticated_client_sme, flag_paa, paa):
    response = jwt_authenticated_client_sme.get('/api/paa/')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 1, len(content["results"])
    assert content["count"] == 1, content["count"]
    assert content["results"][0]["periodo_paa_objeto"]['referencia'] == "Periodo 04/2025 a 10/2025"
    assert content["results"][0]["associacao"] == str(paa.associacao.uuid)


def test_get_por_uuid_sucesso(jwt_authenticated_client_sme, flag_paa, paa):
    response = jwt_authenticated_client_sme.get(f'/api/paa/{paa.uuid}/')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert content["periodo_paa_objeto"]["referencia"] == "Periodo 04/2025 a 10/2025"
    assert content["associacao"] == str(paa.associacao.uuid)


def test_get_404(jwt_authenticated_client_sme, flag_paa, paa):
    response = jwt_authenticated_client_sme.get(f'/api/periodos-paa/c4ce47ec-4ce2-4c34-e2c4-6e24a144fe4e/')

    assert response.status_code == status.HTTP_404_NOT_FOUND
