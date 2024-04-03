import json
from datetime import datetime
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_processo_associacao(
        jwt_authenticated_client_a,
        processo_associacao_123456_2019):

    response = jwt_authenticated_client_a.get(
        f'/api/processos-associacao/{processo_associacao_123456_2019.uuid}/', content_type='application/json')
    result = json.loads(response.content)


    assert response.status_code == status.HTTP_200_OK
    assert result['associacao']['id'] == processo_associacao_123456_2019.associacao.id
    assert result['numero_processo'] == processo_associacao_123456_2019.numero_processo
    assert result['ano'] == processo_associacao_123456_2019.ano
    assert any(periodo['referencia'] == '2019.1' for periodo in result['periodos'])
    assert any(periodo['referencia'] == '2019.2' for periodo in result['periodos'])

    # assert result == esperado


def test_retrieve_processo_associacao_processo_sem_pc_vinculada(jwt_authenticated_client_a, processo_associacao_factory):

    processo_sem_pc_vinculada = processo_associacao_factory.create()
    response = jwt_authenticated_client_a.get(
    f'/api/processos-associacao/{processo_sem_pc_vinculada.uuid}/', content_type='application/json')
    result = json.loads(response.content)

    assert result['permite_exclusao'] == True
    assert result['tooltip_exclusao'] == ''


def test_retrieve_processo_associacao_processo_com_pc_vinculada(jwt_authenticated_client_a, periodo_factory, processo_associacao_factory, prestacao_conta_factory):

    processo_com_pc_vinculada = processo_associacao_factory.create(ano='2023')
    periodo = periodo_factory.create(data_inicio_realizacao_despesas=datetime(2023, 1, 1))
    prestacao_conta_factory.create(periodo=periodo, associacao=processo_com_pc_vinculada.associacao)

    response = jwt_authenticated_client_a.get(
    f'/api/processos-associacao/{processo_com_pc_vinculada.uuid}/', content_type='application/json')
    result = json.loads(response.content)

    assert result['permite_exclusao'] == False
    assert result['tooltip_exclusao'] == 'Não é possível excluir o número desse processo SEI, pois este já está vinculado a uma prestação de contas. Caso necessário, é possível editá-lo.'


def test_retrieve_processo_associacao_multiplos_processos_por_ano(jwt_authenticated_client_a, processo_associacao_factory, periodo_factory, prestacao_conta_factory):

    processo_1 = processo_associacao_factory.create(ano='2023')
    processo_1_2 = processo_associacao_factory.create(associacao=processo_1.associacao, ano=processo_1.ano)

    periodo = periodo_factory.create(data_inicio_realizacao_despesas=datetime(2023, 1, 1))
    prestacao_conta_factory.create(periodo=periodo, associacao=processo_1.associacao)

    # ultimo processo não pode ser excluído
    response = jwt_authenticated_client_a.get(
    f'/api/processos-associacao/{processo_1_2.uuid}/', content_type='application/json')
    result = json.loads(response.content)

    assert result['permite_exclusao'] == False
    assert result['tooltip_exclusao'] == 'Não é possível excluir o número desse processo SEI, pois este já está vinculado a uma prestação de contas. Caso necessário, é possível editá-lo.'

    # processo pode ser excluído se outro for criado para substituir
    response = jwt_authenticated_client_a.get(
    f'/api/processos-associacao/{processo_1.uuid}/', content_type='application/json')
    result = json.loads(response.content)

    assert result['permite_exclusao'] == True
    assert result['tooltip_exclusao'] == ''
