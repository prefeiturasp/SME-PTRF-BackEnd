import pytest
import json
from rest_framework import status
from freezegun import freeze_time
from waffle.testutils import override_flag

pytestmark = pytest.mark.django_db


@override_flag('historico-de-membros', active=True)
@freeze_time('2023-08-08 13:59:00')
def test_action_mandato_anterior(
    mandato_01_2021_a_2022_api,
    mandato_02_2023_a_2025_api,
    associacao,
    jwt_authenticated_client_sme,
):

    mandato_uuid = f"{mandato_01_2021_a_2022_api.uuid}"
    associacao_uuid = f"{associacao.uuid}"

    response = jwt_authenticated_client_sme.get(
        f'/api/mandatos/{mandato_uuid}/mandato-anterior/?associacao_uuid={associacao_uuid}',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


@override_flag('historico-de-membros', active=True)
@freeze_time('2023-08-08 13:59:00')
def test_action_mandato_anterior_sem_composicoes(
    mandato_01_2021_a_2022_api,
    mandato_02_2023_a_2025_api,
    associacao,
    jwt_authenticated_client_sme,
):
    mandato_uuid = f"{mandato_01_2021_a_2022_api.uuid}"
    associacao_uuid = f"{associacao.uuid}"

    response = jwt_authenticated_client_sme.get(
        f'/api/mandatos/{mandato_uuid}/mandato-anterior/?associacao_uuid={associacao_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    # Sem composiçoes para o mandato
    assert len(result['composicoes']) == 0

    assert response.status_code == status.HTTP_200_OK


@override_flag('historico-de-membros', active=True)
@freeze_time('2023-08-08 13:59:00')
def test_action_mandato_anterior_com_composicoes(
    mandato_anterior_01_2021_a_2022_api,
    composicao_anterior_01_2021_a_2022_api,
    associacao,
    jwt_authenticated_client_sme,
):
    mandato_uuid = f"{mandato_anterior_01_2021_a_2022_api.uuid}"
    associacao_uuid = f"{associacao.uuid}"

    response = jwt_authenticated_client_sme.get(
        f'/api/mandatos/{mandato_uuid}/mandato-anterior/?associacao_uuid={associacao_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    # Deve trazer uma composicao
    assert len(result['composicoes']) == 1

    assert response.status_code == status.HTTP_200_OK

