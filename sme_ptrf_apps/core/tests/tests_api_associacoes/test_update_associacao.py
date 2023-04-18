import json

import pytest
from rest_framework import status

from ...models import Associacao

from freezegun import freeze_time

pytestmark = pytest.mark.django_db


def test_api_update_associacao(jwt_authenticated_client_a, associacao):
    payload = {
        "nome": "Nome alterado",
        "processo_regularidade": "123456"
    }
    response = jwt_authenticated_client_a.put(f'/api/associacoes/{associacao.uuid}/', data=json.dumps(payload),
                          content_type='application/json')

    registro_alterado = Associacao.objects.get(uuid=associacao.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert registro_alterado.nome == 'Nome alterado'
    assert registro_alterado.processo_regularidade == '123456'


def test_api_update_associacao_deve_gerar_erro_data_de_encerramento_maior_que_periodo_inicial_data_fim_realizacao_despesas(
    jwt_authenticated_client_a,
    associacao,
    periodo_anterior
):
    with pytest.raises(Exception) as excinfo:
        payload = {
            "nome": "Nome alterado",
            "processo_regularidade": "123456",
            "periodo_inicial": str(periodo_anterior.uuid),
            "data_de_encerramento": "2019-08-29",
        }
        response = jwt_authenticated_client_a.put(f'/api/associacoes/{associacao.uuid}/', data=json.dumps(payload),
                              content_type='application/json')

    assert excinfo.typename == 'ValidationError'

    assert excinfo.value.messages[0] == 'Data de encerramento não pode ser menor que data_fim_realizacao_despesas do período inicial'


@freeze_time('2023-04-18')
def test_api_update_associacao_deve_gerar_erro_data_de_encerramento_maior_que_data_atual(
    jwt_authenticated_client_a,
    associacao,
    periodo_anterior
):
    with pytest.raises(Exception) as excinfo:
        payload = {
            "nome": "Nome alterado",
            "processo_regularidade": "123456",
            "periodo_inicial": str(periodo_anterior.uuid),
            "data_de_encerramento": "2023-04-19",
        }
        response = jwt_authenticated_client_a.put(f'/api/associacoes/{associacao.uuid}/', data=json.dumps(payload),
                              content_type='application/json')

    assert excinfo.typename == 'ValidationError'

    assert excinfo.value.messages[0] == 'Data de encerramento não pode ser maior que a data de Hoje'
