import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_get_sucesso(jwt_authenticated_client_sme, flag_paa, periodo_paa_1):
    response = jwt_authenticated_client_sme.get('/api/periodos-paa/')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 1
    assert content["count"] == 1
    assert content["results"][0]["referencia"] == "Periodo 04/2025 a 10/2025"


def test_get_por_uuid_sucesso(jwt_authenticated_client_sme, flag_paa, periodo_paa_1):
    response = jwt_authenticated_client_sme.get(f'/api/periodos-paa/{periodo_paa_1.uuid}/')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert content["referencia"] == "Periodo 04/2025 a 10/2025"


def test_get_por_referencia_sucesso(jwt_authenticated_client_sme, flag_paa, periodo_paa_1):
    response = jwt_authenticated_client_sme.get('/api/periodos-paa/?referencia=04/2025')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 1
    assert content["count"] == 1
    assert content["results"][0]["referencia"] == "Periodo 04/2025 a 10/2025"


def test_get_por_referencia_sem_resultado(jwt_authenticated_client_sme, flag_paa, periodo_paa_1):
    response = jwt_authenticated_client_sme.get('/api/periodos-paa/?referencia=04/2026')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 0
    assert content["count"] == 0


def test_get_404(jwt_authenticated_client_sme, flag_paa, periodo_paa_1):
    response = jwt_authenticated_client_sme.get('/api/periodos-paa/b737979c-66e2-4d38-b266-652aa1f0fe5d/')

    assert response.status_code == status.HTTP_404_NOT_FOUND
