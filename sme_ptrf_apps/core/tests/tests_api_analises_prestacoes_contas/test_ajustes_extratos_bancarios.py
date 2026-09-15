import json
import uuid

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def analise_conta_prestacao_conta_2020_1(
    prestacao_conta_2020_1_teste_analises,
    analise_prestacao_conta_2020_1_teste_analises,
    conta_associacao_cartao,
):
    return baker.make(
        'AnaliseContaPrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_teste_analises,
        analise_prestacao_conta=analise_prestacao_conta_2020_1_teste_analises,
        conta_associacao=conta_associacao_cartao,
        saldo_extrato=100.00,
    )


def test_api_ajustes_em_extratos_bancarios(
    jwt_authenticated_client_a,
    analise_conta_prestacao_conta_2020_1,
    conta_associacao_cartao,
):
    analise_prestacao = analise_conta_prestacao_conta_2020_1.analise_prestacao_conta

    url = (
        f'/api/analises-prestacoes-contas/{analise_prestacao.uuid}/ajustes-extratos-bancarios/'
        f'?conta_associacao={conta_associacao_cartao.uuid}'
    )

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['uuid'] == str(analise_conta_prestacao_conta_2020_1.uuid)


def test_api_ajustes_em_extratos_bancarios_sem_ajuste(
    jwt_authenticated_client_a,
    analise_prestacao_conta_2020_1_teste_analises,
    conta_associacao_cartao,
):
    url = (
        f'/api/analises-prestacoes-contas/{analise_prestacao_conta_2020_1_teste_analises.uuid}/'
        f'ajustes-extratos-bancarios/?conta_associacao={conta_associacao_cartao.uuid}'
    )

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert response.content == b''


def test_api_ajustes_em_extratos_bancarios_sem_conta_associacao(
    jwt_authenticated_client_a,
    analise_prestacao_conta_2020_1_teste_analises,
):
    url = (
        f'/api/analises-prestacoes-contas/{analise_prestacao_conta_2020_1_teste_analises.uuid}/'
        'ajustes-extratos-bancarios/'
    )

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'parametros_requeridos'


def test_api_ajustes_em_extratos_bancarios_conta_associacao_nao_encontrada(
    jwt_authenticated_client_a,
    analise_prestacao_conta_2020_1_teste_analises,
):
    conta_inexistente = uuid.uuid4()
    url = (
        f'/api/analises-prestacoes-contas/{analise_prestacao_conta_2020_1_teste_analises.uuid}/'
        f'ajustes-extratos-bancarios/?conta_associacao={conta_inexistente}'
    )

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'Objeto não encontrado.'


def test_api_ajustes_em_extratos_bancarios_analise_nao_encontrada(
    jwt_authenticated_client_a,
    conta_associacao_cartao,
):
    analise_inexistente = uuid.uuid4()
    url = (
        f'/api/analises-prestacoes-contas/{analise_inexistente}/'
        f'ajustes-extratos-bancarios/?conta_associacao={conta_associacao_cartao.uuid}'
    )

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'Objeto não encontrado.'
