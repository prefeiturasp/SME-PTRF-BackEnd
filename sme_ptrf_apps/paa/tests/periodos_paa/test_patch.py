from datetime import date
import json
import pytest

from rest_framework import status

from sme_ptrf_apps.paa.models import PeriodoPaa


pytestmark = pytest.mark.django_db


def test_patch_sucesso(jwt_authenticated_client_sme, flag_paa, periodo_paa_1):
    payload = {
        "referencia": "Periodo 007 04/2025 a 10/2025"
    }
    response = jwt_authenticated_client_sme.patch(f'/api/periodos-paa/{periodo_paa_1.uuid}/',
                                                 content_type='application/json',
                                                 data=json.dumps(payload))

    assert response.status_code == status.HTTP_200_OK
    periodos_paa = PeriodoPaa.objects.first()
    assert periodos_paa.referencia == "Periodo 007 04/2025 a 10/2025"


def test_patch_erro_duplicado(jwt_authenticated_client_sme, flag_paa, periodo_paa_1, periodo_paa_2):
    payload = {
        "referencia": "Periodo 11/2025 a 12/2025",
        "data_inicial": "2025-11-01",
        "data_final": "2025-12-31"
    }
    response = jwt_authenticated_client_sme.patch(f'/api/periodos-paa/{periodo_paa_1.uuid}/',
                                                 content_type='application/json',
                                                 data=json.dumps(payload))

    content = json.loads(response.content)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert PeriodoPaa.objects.get(uuid=periodo_paa_1.uuid).referencia == "Periodo 04/2025 a 10/2025"
    assert content["non_field_errors"] == "Referência do PAA já existe."


def test_patch_erro_datas_mesmo_mes_e_ano(jwt_authenticated_client_sme, flag_paa, periodo_paa_1):
    payload = {
        "referencia": "Periodo 04/2025 a 10/2025",
        "data_inicial": "2025-04-02",
        "data_final": "2025-04-30"
    }
    response = jwt_authenticated_client_sme.patch(f'/api/periodos-paa/{periodo_paa_1.uuid}/',
                                                 content_type='application/json',
                                                 data=json.dumps(payload))

    content = json.loads(response.content)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert content["non_field_errors"] == "Data final deve ser maior que a data inicial"


def test_patch_erro_data_final_menor_inicial(jwt_authenticated_client_sme, flag_paa, periodo_paa_1):
    payload = {
        "referencia": "Periodo ABC 04/2025 a 10/2025",
        "data_inicial": "2025-04-02",
        "data_final": "2025-03-30"
    }
    response = jwt_authenticated_client_sme.patch(f'/api/periodos-paa/{periodo_paa_1.uuid}/',
                                                 content_type='application/json',
                                                 data=json.dumps(payload))

    content = json.loads(response.content)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert content["non_field_errors"] == "Data final deve ser maior que a data inicial"


def test_patch_404(jwt_authenticated_client_sme, flag_paa, periodo_paa_1):
    payload = {
        "referencia": "Periodo 007 04/2025 a 10/2025"
    }
    response = jwt_authenticated_client_sme.patch(f'/api/periodos-paa/b737979c-66e2-4d38-b266-652aa1f0fe5d/',
                                                 content_type='application/json',
                                                 data=json.dumps(payload))

    assert response.status_code == status.HTTP_404_NOT_FOUND
