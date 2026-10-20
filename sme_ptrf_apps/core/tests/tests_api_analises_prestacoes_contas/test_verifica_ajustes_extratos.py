import json
import uuid

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_verifica_se_tem_ajustes_extratos_com_ajuste(
    jwt_authenticated_client_a,
    prestacao_conta_2020_1_teste_analises,
    analise_prestacao_conta_2020_1_teste_analises,
    conta_associacao_cartao,
):
    baker.make(
        'AnaliseContaPrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_teste_analises,
        analise_prestacao_conta=analise_prestacao_conta_2020_1_teste_analises,
        conta_associacao=conta_associacao_cartao,
        saldo_extrato=100.00,
    )

    url = (
        f'/api/analises-prestacoes-contas/{analise_prestacao_conta_2020_1_teste_analises.uuid}/'
        f'verifica-ajustes-extratos/'
    )

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_api_verifica_se_tem_ajustes_extratos_sem_ajuste(
    jwt_authenticated_client_a,
    analise_prestacao_conta_2020_1_teste_analises,
):
    url = (
        f'/api/analises-prestacoes-contas/{analise_prestacao_conta_2020_1_teste_analises.uuid}/'
        f'verifica-ajustes-extratos/'
    )

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == []


def test_api_verifica_se_tem_ajustes_extratos_analise_nao_encontrada(
    jwt_authenticated_client_a,
):
    analise_inexistente = uuid.uuid4()
    url = f'/api/analises-prestacoes-contas/{analise_inexistente}/verifica-ajustes-extratos/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'Objeto não encontrado.'
