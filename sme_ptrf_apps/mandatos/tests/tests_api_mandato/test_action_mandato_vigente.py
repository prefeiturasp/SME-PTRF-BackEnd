import pytest
import json
from rest_framework import status
from freezegun import freeze_time
from waffle.testutils import override_flag

pytestmark = pytest.mark.django_db


@override_flag('historico-de-membros', active=True)
@freeze_time('2023-08-08 13:59:00')
def test_action_mandado_vigente(
    mandato_01_2021_a_2022_api,
    mandato_02_2023_a_2025_api,
    jwt_authenticated_client_sme,
    associacao
):
    response = jwt_authenticated_client_sme.get(
        f'/api/mandatos/mandato-vigente/?associacao_uuid={associacao.uuid}',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


@override_flag('historico-de-membros', active=True)
@freeze_time('2023-08-08 13:59:00')
def test_action_mandado_vigente_composicoes_anteriores(
    mandato_2023_a_2025_testes_servicos_01,
    composicao_01_2023_a_2025_testes_servicos,
    composicao_02_2023_a_2025_testes_servicos,
    jwt_authenticated_client_sme,
    associacao
):
    response = jwt_authenticated_client_sme.get(
        f'/api/mandatos/mandato-vigente/?associacao_uuid={associacao.uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK

    assert len(result['composicoes']) == 2


@override_flag('historico-de-membros', active=True)
@freeze_time('2023-08-08 13:59:00')
def test_action_mandado_vigente_sem_mandato_vigente(
    jwt_authenticated_client_sme,
    associacao
):
    response = jwt_authenticated_client_sme.get(
        f'/api/mandatos/mandato-vigente/?associacao_uuid={associacao.uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK

    assert result == {'composicoes': []}


