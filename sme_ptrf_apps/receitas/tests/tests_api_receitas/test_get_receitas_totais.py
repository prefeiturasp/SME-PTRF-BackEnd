import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_receitas_totais_filtro_por_tipo_receita(jwt_authenticated_client_p,
                                                         associacao,
                                                         tipo_receita_estorno):

    response = jwt_authenticated_client_p.get(
        f'/api/receitas/totais/?associacao_uuid={associacao.uuid}&?tipo_receita={tipo_receita_estorno.id}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK


def test_api_get_receitas_totais_filtro_por_acao_associacao(jwt_authenticated_client_p,
                                                            associacao,
                                                            acao_associacao_ptrf):
    response = jwt_authenticated_client_p.get(
        f'/api/receitas/totais/?associacao_uuid={associacao.uuid}&?acao_associacao__uuid={acao_associacao_ptrf.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK


def test_api_get_receitas_totais_filtro_por_conta_associacao(jwt_authenticated_client_p,
                                                            associacao,
                                                            conta_associacao_cheque):
    response = jwt_authenticated_client_p.get(
        f'/api/receitas/totais/?associacao_uuid={associacao.uuid}&?conta_associacao__uuid={conta_associacao_cheque.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK


def test_api_get_receitas_totais_sem_passar_associacao_uuid(jwt_authenticated_client_p):

    response = jwt_authenticated_client_p.get(
        f'/api/receitas/totais/?tipo_receita=7',
        content_type='application/json')
    result = json.loads(response.content)

    results = {
        'erro': 'parametros_requerido',
        'mensagem': 'É necessário enviar o uuid da conta da associação.'
    }

    esperado = results

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado
