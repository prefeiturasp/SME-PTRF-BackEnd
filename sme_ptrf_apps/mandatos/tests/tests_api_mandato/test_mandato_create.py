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


def teste_post_mandato_deve_gerar_erro_data_vigencia_outro_mandato(
    jwt_authenticated_client_sme,
    mandato_02_2023_a_2025_api,
    payload_01_mandato_erro_vigencia_outro_mandato,
):
    response = jwt_authenticated_client_sme.post(
        f'/api/mandatos/',
        data=json.dumps(payload_01_mandato_erro_vigencia_outro_mandato),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == {
        "detail": "A data inicial informada é de vigência de outro mandato cadastrado."
    }


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
