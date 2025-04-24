from datetime import date
import json
import pytest

from rest_framework import status

from sme_ptrf_apps.paa.models import PeriodoPaa


pytestmark = pytest.mark.django_db


def test_post_sucesso(jwt_authenticated_client_sme, flag_paa):
    payload = {
        "referencia": "Periodo 04/2025 a 10/2025",
        "data_inicial": "2025-04-01",
        "data_final": "2025-10-31"
    }
    response = jwt_authenticated_client_sme.post('/api/periodos-paa/',
                                                 content_type='application/json',
                                                 data=json.dumps(payload))

    assert response.status_code == status.HTTP_201_CREATED
    periodos_paa = PeriodoPaa.objects.all()
    assert len(periodos_paa) == 1
    assert periodos_paa[0].referencia == "Periodo 04/2025 a 10/2025"
    assert periodos_paa[0].data_inicial == date(2025, 4, 1)
    assert periodos_paa[0].data_final == date(2025, 10, 31)


def test_post_erro_duplicado(jwt_authenticated_client_sme, flag_paa, periodo_paa_1):
    payload = {
        "referencia": "Periodo 04/2025 a 10/2025",
        "data_inicial": "2025-04-01",
        "data_final": "2025-10-31"
    }
    response = jwt_authenticated_client_sme.post('/api/periodos-paa/',
                                                 content_type='application/json',
                                                 data=json.dumps(payload))

    content = json.loads(response.content)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert PeriodoPaa.objects.count() == 1
    assert content["non_field_errors"] == "Referência do PAA já existe."


def test_post_erro_datas_mesmo_mes_e_ano(jwt_authenticated_client_sme, flag_paa):
    payload = {
        "referencia": "Periodo ABC 04/2025 a 10/2025",
        "data_inicial": "2025-04-02",
        "data_final": "2025-04-30"
    }
    response = jwt_authenticated_client_sme.post('/api/periodos-paa/',
                                                 content_type='application/json',
                                                 data=json.dumps(payload))

    content = json.loads(response.content)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert PeriodoPaa.objects.count() == 0
    assert content["non_field_errors"] == "Data final deve ser maior que a data inicial"


def test_post_erro_data_final_menor_inicial(jwt_authenticated_client_sme, flag_paa):
    payload = {
        "referencia": "Periodo ABC 04/2025 a 10/2025",
        "data_inicial": "2025-04-02",
        "data_final": "2025-03-30"
    }
    response = jwt_authenticated_client_sme.post('/api/periodos-paa/',
                                                 content_type='application/json',
                                                 data=json.dumps(payload))

    content = json.loads(response.content)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert PeriodoPaa.objects.count() == 0
    assert content["non_field_errors"] == "Data final deve ser maior que a data inicial"
