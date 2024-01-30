import pytest
import json
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_resgata_apenas_contas_com_data_inicial(jwt_authenticated_client_a, conta_associacao_factory):

    conta_com_data_inicial = conta_associacao_factory.create()

    conta_sem_data_inicial = conta_associacao_factory.create(
        associacao=conta_com_data_inicial.associacao, data_inicio=None)

    url = f'/api/associacoes/{conta_com_data_inicial.associacao.uuid}/contas/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_api_mostrar_alerta_valores_reprogramados_ao_solicitar(jwt_authenticated_client_a, conta_associacao_factory):

    conta_associacao = conta_associacao_factory.create()

    url = f'/api/associacoes/{conta_associacao.associacao.uuid}/contas/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result[0]['mostrar_alerta_valores_reprogramados_ao_solicitar'] == True


def test_api_nao_mostrar_alerta_valores_reprogramados_ao_solicitar(jwt_authenticated_client_a,
                                                                   associacao_factory,
                                                                   periodo_factory,
                                                                   conta_associacao_factory,
                                                                   prestacao_conta_factory):
    from datetime import datetime
    periodo_2023_1 = periodo_factory.create(data_inicio_realizacao_despesas=datetime(2023, 1, 1),
                                            data_fim_realizacao_despesas=datetime(2023, 5, 30))
    periodo_2023_2 = periodo_factory.create(
        data_inicio_realizacao_despesas=datetime(2023, 6, 1), periodo_anterior=periodo_2023_1)
    associacao = associacao_factory.create(periodo_inicial=periodo_2023_1)
    conta_associacao = conta_associacao_factory.create(associacao=associacao)
    pc = prestacao_conta_factory.create(associacao=conta_associacao.associacao,
                                        periodo=periodo_2023_2)

    url = f'/api/associacoes/{conta_associacao.associacao.uuid}/contas/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result[0]['mostrar_alerta_valores_reprogramados_ao_solicitar'] == False
