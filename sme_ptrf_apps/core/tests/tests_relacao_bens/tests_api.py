import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_previa_relacao_bens(jwt_authenticated_client, periodo, conta_associacao):
    data_inicio = "2019-09-01"
    data_fim = "2019-11-30"
    url = f"/api/relacao-bens/previa/?conta-associacao={conta_associacao.uuid}&periodo={periodo.uuid}&data_inicio={data_inicio}&data_fim={data_fim}"
    response = jwt_authenticated_client.get(url)
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Disposition'][0] == 'attachment; filename=relacao_bens.xlsx'
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Type'][0] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert response.status_code == status.HTTP_200_OK


def test_previa_relacao_bens_data_fim_menor_que_data_inicio(jwt_authenticated_client, periodo, conta_associacao):
    data_inicio = "2019-09-01"
    data_fim = "2019-08-09"
    url = f"/api/relacao-bens/previa/?conta-associacao={conta_associacao.uuid}&periodo={periodo.uuid}&data_inicio={data_inicio}&data_fim={data_fim}"
    response = jwt_authenticated_client.get(url)
    result = response.json()
    esperado = {
        'erro': 'erro_nas_datas',
        'mensagem': 'Data fim não pode ser menor que a data inicio.'
    }
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado


def test_previa_relacao_bens_data_fim_maior_que_data_final_periodo(jwt_authenticated_client, periodo, conta_associacao):
    data_inicio = "2019-09-01"
    data_fim = "2019-12-08"
    url = f"/api/relacao-bens/previa/?conta-associacao={conta_associacao.uuid}&periodo={periodo.uuid}&data_inicio={data_inicio}&data_fim={data_fim}"
    response = jwt_authenticated_client.get(url)
    result = response.json()
    esperado = {
        'erro': 'erro_nas_datas',
        'mensagem': 'Data fim não pode ser maior que a data fim da realização as despesas do periodo.'
    }
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado


def test_previa_relacao_bens_sem_data_inicio_e_data_fim(jwt_authenticated_client, periodo, conta_associacao):
    data_inicio = ""
    data_fim = ""
    url = f"/api/relacao-bens/previa/?conta-associacao={conta_associacao.uuid}&periodo={periodo.uuid}&data_inicio={data_inicio}&data_fim={data_fim}"
    response = jwt_authenticated_client.get(url)
    result = response.json()
    esperado = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar o uuid do período o uuid da conta da associação e as datas de inicio e fim do período.'}
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado
