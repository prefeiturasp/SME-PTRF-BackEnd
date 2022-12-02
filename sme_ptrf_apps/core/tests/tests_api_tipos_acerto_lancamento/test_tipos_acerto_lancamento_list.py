import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_list_tipos_acerto_lancamento(jwt_authenticated_client_a, tipo_acerto_lancamento):
    response = jwt_authenticated_client_a.get(f'/api/tipos-acerto-lancamento/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'ativo': True,
            'id': tipo_acerto_lancamento.id,
            'nome': 'Teste lanca',
            'categoria': 'EXCLUSAO_LANCAMENTO',
            'uuid': f'{tipo_acerto_lancamento.uuid}'
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_tipos_acerto_lancamento_filtro_nome(
    jwt_authenticated_client_a,
    tipo_acerto_lancamento,
    tipo_acerto_lancamento_02,
    tipo_acerto_lancamento_03
):
    response = jwt_authenticated_client_a.get(
        f'/api/tipos-acerto-lancamento/?nome=tes', content_type='application/json'
    )
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'id': tipo_acerto_lancamento.id,
            'nome': tipo_acerto_lancamento.nome,
            'categoria': tipo_acerto_lancamento.categoria,
            'ativo': tipo_acerto_lancamento.ativo,
            'uuid': f'{tipo_acerto_lancamento.uuid}'
        },
        {
            'id': tipo_acerto_lancamento_02.id,
            'nome': tipo_acerto_lancamento_02.nome,
            'categoria': tipo_acerto_lancamento_02.categoria,
            'ativo': tipo_acerto_lancamento_02.ativo,
            'uuid': f'{tipo_acerto_lancamento_02.uuid}'
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_tipos_acerto_lancamento_filtro_categoria(
    jwt_authenticated_client_a,
    tipo_acerto_lancamento,
    tipo_acerto_lancamento_02,
    tipo_acerto_lancamento_03
):
    response = jwt_authenticated_client_a.get(
        f'/api/tipos-acerto-lancamento/?categoria=EDICAO_LANCAMENTO,EXCLUSAO_LANCAMENTO', content_type='application/json'
    )
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'id': tipo_acerto_lancamento.id,
            'nome': tipo_acerto_lancamento.nome,
            'categoria': tipo_acerto_lancamento.categoria,
            'ativo': tipo_acerto_lancamento.ativo,
            'uuid': f'{tipo_acerto_lancamento.uuid}'
        },
        {
            'id': tipo_acerto_lancamento_02.id,
            'nome': tipo_acerto_lancamento_02.nome,
            'categoria': tipo_acerto_lancamento_02.categoria,
            'ativo': tipo_acerto_lancamento_02.ativo,
            'uuid': f'{tipo_acerto_lancamento_02.uuid}'
        },
        {
            'id': tipo_acerto_lancamento_03.id,
            'nome': tipo_acerto_lancamento_03.nome,
            'categoria': tipo_acerto_lancamento_03.categoria,
            'ativo': tipo_acerto_lancamento_03.ativo,
            'uuid': f'{tipo_acerto_lancamento_03.uuid}'
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_tipos_acerto_lancamento_filtro_ativo(
    jwt_authenticated_client_a,
    tipo_acerto_lancamento,
    tipo_acerto_lancamento_02,
    tipo_acerto_lancamento_03
):
    response = jwt_authenticated_client_a.get(
        f'/api/tipos-acerto-lancamento/?ativo=False', content_type='application/json'
    )
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'id': tipo_acerto_lancamento_02.id,
            'nome': tipo_acerto_lancamento_02.nome,
            'categoria': tipo_acerto_lancamento_02.categoria,
            'ativo': tipo_acerto_lancamento_02.ativo,
            'uuid': f'{tipo_acerto_lancamento_02.uuid}'
        },
        {
            'id': tipo_acerto_lancamento_03.id,
            'nome': tipo_acerto_lancamento_03.nome,
            'categoria': tipo_acerto_lancamento_03.categoria,
            'ativo': tipo_acerto_lancamento_03.ativo,
            'uuid': f'{tipo_acerto_lancamento_03.uuid}'
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_tipos_acerto_lancamento_filtro_composto(
    jwt_authenticated_client_a,
    tipo_acerto_lancamento,
    tipo_acerto_lancamento_02,
    tipo_acerto_lancamento_03
):
    response = jwt_authenticated_client_a.get(
        f'/api/tipos-acerto-lancamento/?nome=lan&categoria=EXCLUSAO_LANCAMENTO', content_type='application/json'
    )
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'id': tipo_acerto_lancamento.id,
            'nome': tipo_acerto_lancamento.nome,
            'categoria': tipo_acerto_lancamento.categoria,
            'ativo': tipo_acerto_lancamento.ativo,
            'uuid': f'{tipo_acerto_lancamento.uuid}'
        },
        {
            'id': tipo_acerto_lancamento_03.id,
            'nome': tipo_acerto_lancamento_03.nome,
            'categoria': tipo_acerto_lancamento_03.categoria,
            'ativo': tipo_acerto_lancamento_03.ativo,
            'uuid': f'{tipo_acerto_lancamento_03.uuid}'
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
