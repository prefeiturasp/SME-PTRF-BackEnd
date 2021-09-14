import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def especificacao_custeio_material_eletrico(tipo_aplicacao_recurso_custeio, tipo_custeio_material):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Material elétrico',
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
    )


@pytest.fixture
def especificacao_custeio_servico_instalacao_eletrica(tipo_aplicacao_recurso_custeio, tipo_custeio_servico):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Instalação elétrica',
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
    )


@pytest.fixture
def especificacao_capital_ar_condicionado(tipo_aplicacao_recurso_capital):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Ar condicionado',
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
    )


@pytest.fixture
def json_especificacao_custeio_material_eletrico(especificacao_custeio_material_eletrico):
    return {
        'id': especificacao_custeio_material_eletrico.id,
        'descricao': especificacao_custeio_material_eletrico.descricao,
        'aplicacao_recurso': especificacao_custeio_material_eletrico.aplicacao_recurso,
        'tipo_custeio': especificacao_custeio_material_eletrico.tipo_custeio.id,
        'ativa': True,

    }


@pytest.fixture
def json_especificacao_custeio_servico_instalacao_eletrica(especificacao_custeio_servico_instalacao_eletrica):
    return {
        'id': especificacao_custeio_servico_instalacao_eletrica.id,
        'descricao': especificacao_custeio_servico_instalacao_eletrica.descricao,
        'aplicacao_recurso': especificacao_custeio_servico_instalacao_eletrica.aplicacao_recurso,
        'tipo_custeio': especificacao_custeio_servico_instalacao_eletrica.tipo_custeio.id,
        'ativa': True,
    }


@pytest.fixture
def json_especificacao_capital_ar_condicionado(especificacao_capital_ar_condicionado):
    return {
        'id': especificacao_capital_ar_condicionado.id,
        'descricao': especificacao_capital_ar_condicionado.descricao,
        'aplicacao_recurso': especificacao_capital_ar_condicionado.aplicacao_recurso,
        'tipo_custeio': None,
        'ativa': True,
    }


def test_api_get_especificacoes_sem_filtro(jwt_authenticated_client, json_especificacao_custeio_material_eletrico,
                                           json_especificacao_custeio_servico_instalacao_eletrica,
                                           json_especificacao_capital_ar_condicionado):
    response = jwt_authenticated_client.get('/api/especificacoes/', content_type='application/json')
    result = json.loads(response.content)

    esperado = [
        json_especificacao_capital_ar_condicionado,
        json_especificacao_custeio_servico_instalacao_eletrica,
        json_especificacao_custeio_material_eletrico,

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_api_get_especificacoes_com_filtro_capital(jwt_authenticated_client, json_especificacao_custeio_material_eletrico,
                                                   json_especificacao_custeio_servico_instalacao_eletrica,
                                                   json_especificacao_capital_ar_condicionado):
    response = jwt_authenticated_client.get('/api/especificacoes/?aplicacao_recurso=CAPITAL', content_type='application/json')
    result = json.loads(response.content)

    esperado = [
        json_especificacao_capital_ar_condicionado,

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_api_get_especificacoes_com_filtro_custeio(jwt_authenticated_client, json_especificacao_custeio_material_eletrico,
                                                   json_especificacao_custeio_servico_instalacao_eletrica,
                                                   json_especificacao_capital_ar_condicionado):
    response = jwt_authenticated_client.get('/api/especificacoes/?aplicacao_recurso=CUSTEIO', content_type='application/json')
    result = json.loads(response.content)

    esperado = [
        json_especificacao_custeio_servico_instalacao_eletrica,
        json_especificacao_custeio_material_eletrico,
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_api_get_especificacoes_com_filtro_custeio_servico(jwt_authenticated_client, json_especificacao_custeio_material_eletrico,
                                                           json_especificacao_custeio_servico_instalacao_eletrica,
                                                           json_especificacao_capital_ar_condicionado,
                                                           tipo_custeio_servico):
    response = jwt_authenticated_client.get(f'/api/especificacoes/?aplicacao_recurso=CUSTEIO&tipo_custeio={tipo_custeio_servico.id}',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = [
        json_especificacao_custeio_servico_instalacao_eletrica,
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
