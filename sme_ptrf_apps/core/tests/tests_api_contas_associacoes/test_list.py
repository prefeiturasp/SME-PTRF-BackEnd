import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_list_contas_associacoes(
    jwt_authenticated_client_a,
    conta_associacao_1
):
    response = jwt_authenticated_client_a.get(f'/api/contas-associacoes/', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result["results"]) == 1
    assert result["results"][0]["uuid"] == str(conta_associacao_1.uuid)
    assert result["results"][0]["tipo_conta_dados"]["uuid"] == str(conta_associacao_1.tipo_conta.uuid)
    assert result["results"][0]["associacao_dados"]["uuid"] == str(conta_associacao_1.associacao.uuid)


def test_list_contas_associacoes_filtro_nome_associacao_sucesso(
    jwt_authenticated_client_a,
    conta_associacao_1
):
    response = jwt_authenticated_client_a.get(
        f'/api/contas-associacoes/?associacao_nome={conta_associacao_1.associacao.nome}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result["results"]) == 1
    assert result["results"][0]["uuid"] == str(conta_associacao_1.uuid)
    assert result["results"][0]["tipo_conta_dados"]["uuid"] == str(conta_associacao_1.tipo_conta.uuid)
    assert result["results"][0]["associacao_dados"]["uuid"] == str(conta_associacao_1.associacao.uuid)


def test_list_contas_associacoes_filtro_nome_associacao_nao_encontrado(
    jwt_authenticated_client_a,
    conta_associacao_1
):
    response = jwt_authenticated_client_a.get(
        f'/api/contas-associacoes/?associacao_nome=nome_aleatorio',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result["results"]) == 0


def test_list_contas_associacoes_filtro_nome_tipo_conta_sucesso(
    jwt_authenticated_client_a,
    conta_associacao_1
):
    response = jwt_authenticated_client_a.get(
        f'/api/contas-associacoes/?tipo_conta_nome={conta_associacao_1.tipo_conta.nome}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result["results"]) == 1
    assert result["results"][0]["uuid"] == str(conta_associacao_1.uuid)
    assert result["results"][0]["tipo_conta_dados"]["uuid"] == str(conta_associacao_1.tipo_conta.uuid)
    assert result["results"][0]["associacao_dados"]["uuid"] == str(conta_associacao_1.associacao.uuid)


def test_list_contas_associacoes_filtro_nome_tipo_conta_nao_encontrado(
    jwt_authenticated_client_a,
    conta_associacao_1
):
    response = jwt_authenticated_client_a.get(
        f'/api/contas-associacoes/?tipo_conta_uuid=c636046a-8d67-49a0-9a4c-92b0af480000',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result["results"]) == 0


def test_list_contas_associacoes_filtro_status_sucesso(
    jwt_authenticated_client_a,
    conta_associacao_1,
    conta_associacao_2
):
    response = jwt_authenticated_client_a.get(
        f'/api/contas-associacoes/?status={conta_associacao_2.status}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result["results"]) == 2
    assert result["results"][0]["uuid"] == str(conta_associacao_1.uuid)
    assert result["results"][0]["tipo_conta_dados"]["uuid"] == str(conta_associacao_1.tipo_conta.uuid)
    assert result["results"][0]["associacao_dados"]["uuid"] == str(conta_associacao_1.associacao.uuid)
    assert result["results"][1]["uuid"] == str(conta_associacao_2.uuid)
    assert result["results"][1]["tipo_conta_dados"]["uuid"] == str(conta_associacao_2.tipo_conta.uuid)
    assert result["results"][1]["associacao_dados"]["uuid"] == str(conta_associacao_2.associacao.uuid)


def test_list_contas_associacoes_filtro_status_nao_encontrado(
    jwt_authenticated_client_a,
    conta_associacao_1
):
    response = jwt_authenticated_client_a.get(
        '/api/contas-associacoes/?status=nome_aleatorio',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result["results"]) == 0


def test_list_contas_associacoes_filtro_nome_associacao_e_nome_tipo_conta_sucesso(
    jwt_authenticated_client_a,
    conta_associacao_1
):
    response = jwt_authenticated_client_a.get(
        f'/api/contas-associacoes/?associacao_nome={conta_associacao_1.associacao.nome}&tipo_conta_uuid={conta_associacao_1.tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result["results"]) == 1
    assert result["results"][0]["uuid"] == str(conta_associacao_1.uuid)
    assert result["results"][0]["tipo_conta_dados"]["uuid"] == str(conta_associacao_1.tipo_conta.uuid)
    assert result["results"][0]["associacao_dados"]["uuid"] == str(conta_associacao_1.associacao.uuid)


def test_list_contas_associacoes_filtro_nome_associacao_e_nome_tipo_conta_nao_encontrado(
    jwt_authenticated_client_a,
    conta_associacao_1
):
    response = jwt_authenticated_client_a.get(
        f'/api/contas-associacoes/?associacao_nome={conta_associacao_1.associacao.nome}&tipo_conta_uuid=c636046a-8d67-49a0-9a4c-0000af48ea50',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result["results"]) == 0


def test_list_contas_associacoes_filtro_nome_associacao_e_status_sucesso(
    jwt_authenticated_client_a,
    conta_associacao_2
):
    response = jwt_authenticated_client_a.get(
        f'/api/contas-associacoes/?associacao_nome={conta_associacao_2.associacao.nome}&status={conta_associacao_2.status}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result["results"]) == 1
    assert result["results"][0]["uuid"] == str(conta_associacao_2.uuid)
    assert result["results"][0]["tipo_conta_dados"]["uuid"] == str(conta_associacao_2.tipo_conta.uuid)
    assert result["results"][0]["associacao_dados"]["uuid"] == str(conta_associacao_2.associacao.uuid)


def test_list_contas_associacoes_filtro_nome_associacao_e_status_nao_encontrado(
    jwt_authenticated_client_a,
    conta_associacao_2
):
    response = jwt_authenticated_client_a.get(
        f'/api/contas-associacoes/?associacao_nome={conta_associacao_2.associacao.nome}&status=status_aleatorio',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result["results"]) == 0


def test_list_contas_associacoes_filtro_todos_sucesso(
    jwt_authenticated_client_a,
    conta_associacao_2
):
    response = jwt_authenticated_client_a.get(
        f'/api/contas-associacoes/?associacao_nome={conta_associacao_2.associacao.nome}&tipo_conta_nome={conta_associacao_2.tipo_conta.nome}&status={conta_associacao_2.status}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result["results"]) == 1
    assert result["results"][0]["uuid"] == str(conta_associacao_2.uuid)
    assert result["results"][0]["tipo_conta_dados"]["uuid"] == str(conta_associacao_2.tipo_conta.uuid)
    assert result["results"][0]["associacao_dados"]["uuid"] == str(conta_associacao_2.associacao.uuid)


def test_list_contas_associacoes_filtro_todos_nao_encontrado(
    jwt_authenticated_client_a,
    conta_associacao_2
):
    response = jwt_authenticated_client_a.get(
        f'/api/contas-associacoes/?associacao_nome={conta_associacao_2.associacao.nome}&tipo_conta_uuid=c636046a-8d67-49a0-9a4c-0666af48ea50&status={conta_associacao_2.status}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result["results"]) == 0
