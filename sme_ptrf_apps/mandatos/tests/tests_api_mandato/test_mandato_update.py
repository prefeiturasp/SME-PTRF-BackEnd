import json
import pytest
from datetime import date
from rest_framework import status

from sme_ptrf_apps.mandatos.models import Mandato

pytestmark = pytest.mark.django_db


def teste_patch_mandato(
    jwt_authenticated_client_sme,
    mandato_01_2021_a_2022_api,
    payload_01_update_mandato,
):
    uuid_mandato = f'{mandato_01_2021_a_2022_api.uuid}'

    assert mandato_01_2021_a_2022_api.referencia_mandato == '2021 a 2022'
    assert mandato_01_2021_a_2022_api.data_inicial == date(2021, 1, 1)
    assert mandato_01_2021_a_2022_api.data_final == date(2022, 12, 31)

    response = jwt_authenticated_client_sme.patch(
        f'/api/mandatos/{uuid_mandato}/',
        data=json.dumps(payload_01_update_mandato),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK

    mandato_alterado = Mandato.objects.get(uuid=uuid_mandato)

    assert mandato_alterado.referencia_mandato == '2028 a 2029'
    assert mandato_alterado.data_inicial == date(2028, 1, 1)
    assert mandato_alterado.data_final == date(2029, 12, 31)


def teste_path_mandato_deve_gerar_erro_data_vigencia_outro_mandato(
    jwt_authenticated_client_sme,
    mandato_02_2023_a_2025_api,
    mandato_01_2021_a_2022_api,
    payload_02_mandato_erro_vigencia_outro_mandato,
):
    uuid_mandato = f'{mandato_02_2023_a_2025_api.uuid}'

    response = jwt_authenticated_client_sme.patch(
        f'/api/mandatos/{uuid_mandato}/',
        data=json.dumps(payload_02_mandato_erro_vigencia_outro_mandato),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == {
        "detail": "A data inicial informada é de vigência de outro mandato cadastrado."
    }


def teste_post_mandato_deve_gerar_erro_data_final_menor_que_data_inicial(
    jwt_authenticated_client_sme,
    mandato_02_2023_a_2025_api,
    payload_01_mandato_erro_data_final_maior_que_data_inical,
):
    uuid_mandato = f'{mandato_02_2023_a_2025_api.uuid}'

    response = jwt_authenticated_client_sme.patch(
        f'/api/mandatos/{uuid_mandato}/',
        data=json.dumps(payload_01_mandato_erro_data_final_maior_que_data_inical),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == {
        "detail": "A data final não pode ser menor que a data inicial"
    }
