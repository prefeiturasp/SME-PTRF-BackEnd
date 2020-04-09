import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def json_especificacao_custeio_material(especificacao_custeio_material):
    return {
        'id': especificacao_custeio_material.id,
        'descricao': especificacao_custeio_material.descricao,
        'aplicacao_recurso': especificacao_custeio_material.aplicacao_recurso,
        'tipo_custeio': especificacao_custeio_material.tipo_custeio.id

    }


@pytest.fixture
def json_especificacao_custeio_servico(especificacao_custeio_servico):
    return {
        'id': especificacao_custeio_servico.id,
        'descricao': especificacao_custeio_servico.descricao,
        'aplicacao_recurso': especificacao_custeio_servico.aplicacao_recurso,
        'tipo_custeio': especificacao_custeio_servico.tipo_custeio.id
    }


@pytest.fixture
def json_especificacao_capital(especificacao_capital):
    return {
        'id': especificacao_capital.id,
        'descricao': especificacao_capital.descricao,
        'aplicacao_recurso': especificacao_capital.aplicacao_recurso,
        'tipo_custeio': None
    }


def test_api_get_especificacoes_sem_filtro(client, json_especificacao_custeio_material,
                                           json_especificacao_custeio_servico, json_especificacao_capital):
    response = client.get('/api/especificacoes/', content_type='application/json')
    result = json.loads(response.content)

    esperado = [
        json_especificacao_custeio_material,
        json_especificacao_custeio_servico,
        json_especificacao_capital,

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_api_get_especificacoes_com_filtro_capital(client, json_especificacao_custeio_material,
                                                   json_especificacao_custeio_servico, json_especificacao_capital):
    response = client.get('/api/especificacoes/?aplicacao_recurso=CAPITAL', content_type='application/json')
    result = json.loads(response.content)

    esperado = [
        json_especificacao_capital,

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_api_get_especificacoes_com_filtro_custeio(client, json_especificacao_custeio_material,
                                                   json_especificacao_custeio_servico, json_especificacao_capital):
    response = client.get('/api/especificacoes/?aplicacao_recurso=CUSTEIO', content_type='application/json')
    result = json.loads(response.content)

    esperado = [
        json_especificacao_custeio_material,
        json_especificacao_custeio_servico,
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_api_get_especificacoes_com_filtro_custeio_servico(client, json_especificacao_custeio_material,
                                                           json_especificacao_custeio_servico,
                                                           json_especificacao_capital, tipo_custeio_servico):
    response = client.get(f'/api/especificacoes/?aplicacao_recurso=CUSTEIO&tipo_custeio={tipo_custeio_servico.id}',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = [
        json_especificacao_custeio_servico,
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
