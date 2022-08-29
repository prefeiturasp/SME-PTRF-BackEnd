import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

@pytest.fixture
def payload_publicar_consolidado_de_publicacoes_parciais(dre_teste_api_consolidado_dre, periodo_teste_api_consolidado_dre):
    payload = {
        'dre_uuid': f'{dre_teste_api_consolidado_dre.uuid}',
        'periodo_uuid': f'{periodo_teste_api_consolidado_dre.uuid}',
    }
    return payload


@pytest.fixture
def payload_publicar_consolidado_de_publicacoes_parciais_sem_dre(periodo_teste_api_consolidado_dre):
    payload = {
        'periodo_uuid': f'{periodo_teste_api_consolidado_dre.uuid}',
    }
    return payload


@pytest.fixture
def payload_publicar_consolidado_de_publicacoes_parciais_sem_periodo(dre_teste_api_consolidado_dre):
    payload = {
        'dre_uuid': f'{dre_teste_api_consolidado_dre.uuid}',
    }
    return payload


@pytest.fixture
def retorna_parcial():
    parcial = {
        "parcial": False,
        "sequencia_de_publicacao_atual": None,
    }
    return parcial


@pytest.fixture
def retorna_parcial_apenas_nao_publicadas():
    apenas_nao_publicadas=False,
    return apenas_nao_publicadas


def test_action_gerar_consolidado_de_publicacoes_parciais_deve_retornar_status_200(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    payload_publicar_consolidado_de_publicacoes_parciais,
    consolidado_dre_teste_api_consolidado_dre
):
    response = jwt_authenticated_client_dre.post(
        '/api/consolidados-dre/gerar-consolidado-de-publicacoes-parciais/',
        data=json.dumps(payload_publicar_consolidado_de_publicacoes_parciais),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


def test_action_gerar_consolidado_de_publicacoes_parciais_sem_dre_deve_retornar_erro(
    jwt_authenticated_client_dre,
    periodo_teste_api_consolidado_dre,
    payload_publicar_consolidado_de_publicacoes_parciais_sem_dre,
    consolidado_dre_teste_api_consolidado_dre
):
    response = jwt_authenticated_client_dre.post(
        '/api/consolidados-dre/gerar-consolidado-de-publicacoes-parciais/',
        data=json.dumps(payload_publicar_consolidado_de_publicacoes_parciais_sem_dre),
        content_type='application/json'
    )

    result = json.loads(response.content)

    erro = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar os uuids da dre e período'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == erro


def test_action_gerar_consolidado_de_publicacoes_parciais_sem_periodo_deve_retornar_erro(
    jwt_authenticated_client_dre,
    periodo_teste_api_consolidado_dre,
    payload_publicar_consolidado_de_publicacoes_parciais_sem_periodo,
    consolidado_dre_teste_api_consolidado_dre
):
    response = jwt_authenticated_client_dre.post(
        '/api/consolidados-dre/gerar-consolidado-de-publicacoes-parciais/',
        data=json.dumps(payload_publicar_consolidado_de_publicacoes_parciais_sem_periodo),
        content_type='application/json'
    )

    result = json.loads(response.content)

    erro = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar os uuids da dre e período'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == erro



