import pytest
import json
import uuid
from rest_framework import status
from django.utils import timezone
from waffle.testutils import override_flag

pytestmark = pytest.mark.django_db

@override_flag('historico-de-membros', active=True)
def test_action_ocupantes_e_cargos_da_composicao_200_ok(
    jwt_authenticated_client_sme,
    associacao,
    composicao_03_testes_service_data_saida_do_cargo_nao_deve_criar_nova_composicao,
):
    data_param = timezone.now().date().isoformat()

    response = jwt_authenticated_client_sme.get(
        f'/api/cargos-composicao/composicao-por-data/?associacao_uuid={associacao.uuid}&data={data_param}',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK

@override_flag('historico-de-membros', active=True)
def test_action_ocupantes_associacao_nao_encontrada(jwt_authenticated_client_sme):
    data_param = "2025-01-01"
    uuid_inexistente = uuid.uuid4()

    response = jwt_authenticated_client_sme.get(
        f'/api/cargos-composicao/composicao-por-data/?associacao_uuid={uuid_inexistente}&data={data_param}',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "associacao_uuid" in response.json()

@override_flag('historico-de-membros', active=True)
def test_action_ocupantes_composicao_nao_encontrada(jwt_authenticated_client_sme, associacao):
    data_param = "1900-01-01"

    response = jwt_authenticated_client_sme.get(
        f'/api/cargos-composicao/composicao-por-data/?associacao_uuid={associacao.uuid}&data={data_param}',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Composição não encontrada" in response.json().get("erro", "")

@override_flag('historico-de-membros', active=True)
def test_action_ocupantes_dados_invalidos(jwt_authenticated_client_sme):
    response = jwt_authenticated_client_sme.get(
        '/api/cargos-composicao/composicao-por-data/?associacao_uuid=valor_invalido&data=data_errada',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_data = response.json()
    assert "associacao_uuid" in response_data
    assert "data" in response_data

@override_flag('historico-de-membros', active=True)
def test_mais_de_uma_composicao_para_data(
    jwt_authenticated_client_sme,
    associacao, 
    composicao_03_testes_service_data_saida_do_cargo_nao_deve_criar_nova_composicao,
    composicao_01_testes_service_data_saida_do_cargo
):
    data_param = "2025-01-01"

    response = jwt_authenticated_client_sme.get(
        f'/api/cargos-composicao/composicao-por-data/?associacao_uuid={associacao.uuid}&data={data_param}',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"erro": "Mais de uma composição encontrada para a data informada."}
