import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def teste_post_mandato(
    jwt_authenticated_client_sme,
    payload_01_mandato,
):
    response = jwt_authenticated_client_sme.post(
        f'/api/mandatos/',
        data=json.dumps(payload_01_mandato),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_201_CREATED


def teste_post_mandato_deve_gerar_erro_data_final_menor_que_data_inicial(
    jwt_authenticated_client_sme,
    payload_01_mandato_erro_data_final_maior_que_data_inical,
):
    response = jwt_authenticated_client_sme.post(
        f'/api/mandatos/',
        data=json.dumps(payload_01_mandato_erro_data_final_maior_que_data_inical),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == {
        "detail": "A data final não pode ser menor que a data inicial"
    }


def teste_post_mandato_deve_gerar_erro_data_inicial_menor_que_data_final_mandato_anterior(
    jwt_authenticated_client_sme,
    payload_mandato_erro_data_inicial_menor_que_data_final_mandato_anterior,
    mandato_01_2021_a_2022_api,
):
    response = jwt_authenticated_client_sme.post(
        f'/api/mandatos/',
        data=json.dumps(payload_mandato_erro_data_inicial_menor_que_data_final_mandato_anterior),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == {
        "detail": "A data inicial do período de mandato deve ser maior que a data final do mandato anterior"
    }
