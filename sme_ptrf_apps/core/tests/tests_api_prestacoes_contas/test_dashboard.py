import json

import pytest
from rest_framework import status
from model_bakery import baker

pytestmark = pytest.mark.django_db


@pytest.fixture
def prestacao_conta1(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        status="EM_ANALISE"
    )


@pytest.fixture
def prestacao_conta2(periodo, outra_associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=outra_associacao,
        status="APROVADA"
    )


@pytest.fixture
def associacao_3(unidade, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Terceira',
        cnpj='52.302.275/0001-00',
        unidade=unidade,
        periodo_inicial=periodo_anterior,
    )


@pytest.fixture
def prestacao_conta3(periodo, associacao_3):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao_3,
        status="APROVADA_RESSALVA"
    )


def test_dashboard(
    jwt_authenticated_client_a,
    prestacao_conta1,
    prestacao_conta2,
    prestacao_conta3,
    periodo,
    dre
):
    response = jwt_authenticated_client_a.get(
        f"/api/prestacoes-contas/dashboard/?periodo={periodo.uuid}&dre_uuid={dre.uuid}")
    result = response.json()

    esperado = {
        'total_associacoes_dre': 3,
        'cards': [
            {
                'titulo': 'Prestações de contas não recebidas',
                'quantidade_prestacoes': 0,
                'status': 'NAO_RECEBIDA'},
            {
                'titulo': 'Prestações de contas recebidas aguardando análise',
                'quantidade_prestacoes': 0,
                'status': 'RECEBIDA'},
            {
                'titulo': 'Prestações de contas em análise',
                'quantidade_prestacoes': 1,
                'status': 'EM_ANALISE'},
            {
                'titulo': 'Prestações de conta devolvidas para acertos',
                'quantidade_prestacoes': 0,
                'status': 'DEVOLVIDA'},
            {
                'titulo': 'Prestações de contas aprovadas',
                'quantidade_prestacoes': 1,
                'status': 'APROVADA'},
            {
                'titulo': 'Prestações de contas reprovadas',
                'quantidade_prestacoes': 0,
                'status': 'REPROVADA'}
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert esperado == result


def test_dashboard_add_aprovada_ressalva(
    jwt_authenticated_client_a,
    prestacao_conta1,
    prestacao_conta2,
    prestacao_conta3,
    periodo,
    dre
):
    response = jwt_authenticated_client_a.get(
        f"/api/prestacoes-contas/dashboard/?periodo={periodo.uuid}&dre_uuid={dre.uuid}&add_aprovadas_ressalva=SIM")
    result = response.json()

    esperado = {
        'total_associacoes_dre': 3,
        'cards': [
            {
                'titulo': 'Prestações de contas não recebidas',
                'quantidade_prestacoes': 0,
                'status': 'NAO_RECEBIDA'},
            {
                'titulo': 'Prestações de contas recebidas aguardando análise',
                'quantidade_prestacoes': 0,
                'status': 'RECEBIDA'},
            {
                'titulo': 'Prestações de contas em análise',
                'quantidade_prestacoes': 1,
                'status': 'EM_ANALISE'},
            {
                'titulo': 'Prestações de conta devolvidas para acertos',
                'quantidade_prestacoes': 0,
                'status': 'DEVOLVIDA'},
            {
                'titulo': 'Prestações de contas aprovadas',
                'quantidade_prestacoes': 1,
                'status': 'APROVADA'},
            {
                'titulo': 'Prestações de contas reprovadas',
                'quantidade_prestacoes': 0,
                'status': 'REPROVADA'},
            {
                'titulo': 'Prestações de contas aprovadas com ressalvas',
                'quantidade_prestacoes': 1,
                'status': 'APROVADA_RESSALVA'}
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_dashboard_erro(jwt_authenticated_client_a, prestacao_conta1, prestacao_conta2, periodo, dre):
    response = jwt_authenticated_client_a.get(f"/api/prestacoes-contas/dashboard/?periodo=&dre_uuid=")
    result = response.json()

    erro_esperado = {
        'erro': 'parametros_requerido',
        'mensagem': 'É necessário enviar o uuid da dre (dre_uuid) e o periodo como parâmetros.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert erro_esperado == result


def test_dashboard_outro_periodo(jwt_authenticated_client_a, prestacao_conta1, prestacao_conta2, periodo_2020_1, dre):
    response = jwt_authenticated_client_a.get(
        f"/api/prestacoes-contas/dashboard/?periodo={periodo_2020_1.uuid}&dre_uuid={dre.uuid}")
    result = response.json()

    esperado = {
        'total_associacoes_dre': 2,
        'cards': [
            {
                'titulo': 'Prestações de contas não recebidas',
                'quantidade_prestacoes': 0,
                'status': 'NAO_RECEBIDA'},
            {
                'titulo': 'Prestações de contas recebidas aguardando análise',
                'quantidade_prestacoes': 0,
                'status': 'RECEBIDA'},
            {
                'titulo': 'Prestações de contas em análise',
                'quantidade_prestacoes': 0,
                'status': 'EM_ANALISE'},
            {
                'titulo': 'Prestações de conta devolvidas para acertos',
                'quantidade_prestacoes': 0,
                'status': 'DEVOLVIDA'},
            {
                'titulo': 'Prestações de contas aprovadas',
                'quantidade_prestacoes': 0,
                'status': 'APROVADA'},
            {
                'titulo': 'Prestações de contas reprovadas',
                'quantidade_prestacoes': 0,
                'status': 'REPROVADA'}
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert esperado == result
