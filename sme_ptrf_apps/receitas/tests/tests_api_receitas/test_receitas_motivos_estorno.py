import json

import pytest
from rest_framework import status

from model_bakery import baker

from ...models import Receita

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_receita_estorno_motivos(tipo_conta):
    return baker.make('TipoReceita', nome='Estorno', e_estorno=True, tipos_conta=[tipo_conta])


@pytest.fixture
def receita_estorno_motivos(tipo_receita_estorno_motivos, rateio_no_periodo_100_custeio):
    rateio = rateio_no_periodo_100_custeio
    return baker.make(
        'Receita',
        associacao=rateio.despesa.associacao,
        data=rateio.despesa.data_transacao,
        valor=rateio.valor_rateio,
        conta_associacao=rateio.conta_associacao,
        acao_associacao=rateio.acao_associacao,
        tipo_receita=tipo_receita_estorno_motivos,
        conferido=True,
        categoria_receita=rateio.aplicacao_recurso,
        rateio_estornado=rateio
    )


@pytest.fixture
def payload_receita_com_motivos_estorno_e_outros_motivos(
    associacao,
    tipo_receita_estorno_motivos,
    acao_associacao,
    conta_associacao,
    detalhe_tipo_receita,
    motivo_estorno_01,
    motivo_estorno_02
):

    payload = {
        "acao_associacao": str(acao_associacao.uuid),
        "associacao": str(associacao.uuid),
        "categoria_receita": "CAPITAL",
        "conta_associacao": str(conta_associacao.uuid),
        "data": "2022-03-23",
        "detalhe_outros": "",
        "detalhe_tipo_receita": "",
        "saida_do_recurso": "",
        "tipo_receita": str(tipo_receita_estorno_motivos.id),
        "valor": 100.00,
        "rateio_estornado": None,
        "motivos_estorno": [motivo_estorno_01.id, motivo_estorno_02.id],
        "outros_motivos_estorno": 'Outros motivos estorno',
    }

    return payload


@pytest.fixture
def payload_receita_com_motivos_estorno_e_sem_outros_motivos(
    associacao,
    tipo_receita_estorno_motivos,
    acao_associacao,
    conta_associacao,
    detalhe_tipo_receita,
    motivo_estorno_01,
    motivo_estorno_02
):

    payload = {
        "acao_associacao": str(acao_associacao.uuid),
        "associacao": str(associacao.uuid),
        "categoria_receita": "CAPITAL",
        "conta_associacao": str(conta_associacao.uuid),
        "data": "2022-03-23",
        "detalhe_outros": "",
        "detalhe_tipo_receita": "",
        "saida_do_recurso": "",
        "tipo_receita": str(tipo_receita_estorno_motivos.id),
        "valor": 100.00,
        "rateio_estornado": None,
        "motivos_estorno": [motivo_estorno_01.id, motivo_estorno_02.id],
    }

    return payload


@pytest.fixture
def payload_receita_sem_motivos_estorno_e_com_outros_motivos(
    associacao,
    tipo_receita_estorno_motivos,
    acao_associacao,
    conta_associacao,
    detalhe_tipo_receita,
    motivo_estorno_01,
    motivo_estorno_02
):

    payload = {
        "acao_associacao": str(acao_associacao.uuid),
        "associacao": str(associacao.uuid),
        "categoria_receita": "CAPITAL",
        "conta_associacao": str(conta_associacao.uuid),
        "data": "2022-03-23",
        "detalhe_outros": "",
        "detalhe_tipo_receita": "",
        "saida_do_recurso": "",
        "tipo_receita": str(tipo_receita_estorno_motivos.id),
        "valor": 100.00,
        "rateio_estornado": None,
        "outros_motivos_estorno": 'Outros motivos estorno',
    }

    return payload


@pytest.fixture
def payload_receita_sem_motivos_estorno_e_sem_outros_motivos(
    associacao,
    tipo_receita_estorno_motivos,
    acao_associacao,
    conta_associacao,
    detalhe_tipo_receita,
):

    payload = {
        "acao_associacao": str(acao_associacao.uuid),
        "associacao": str(associacao.uuid),
        "categoria_receita": "CAPITAL",
        "conta_associacao": str(conta_associacao.uuid),
        "data": "2022-03-23",
        "detalhe_outros": "",
        "detalhe_tipo_receita": "",
        "saida_do_recurso": "",
        "tipo_receita": str(tipo_receita_estorno_motivos.id),
        "valor": 100.00,
        "rateio_estornado": None,
    }

    return payload


def test_post_receita_com_motivos_estorno_e_outros_motivos_estorno(
    payload_receita_com_motivos_estorno_e_outros_motivos,
    jwt_authenticated_client_p,
    motivo_estorno_01,
    motivo_estorno_02
):

    response = jwt_authenticated_client_p.post('/api/receitas/', data=json.dumps(
        payload_receita_com_motivos_estorno_e_outros_motivos), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert result['motivos_estorno'] == [motivo_estorno_01.id, motivo_estorno_02.id]
    assert result['outros_motivos_estorno'] == "Outros motivos estorno"


def test_post_receita_com_motivos_estorno_e_sem_outros_motivos_estorno(
    payload_receita_com_motivos_estorno_e_sem_outros_motivos,
    jwt_authenticated_client_p,
    motivo_estorno_01,
    motivo_estorno_02
):

    response = jwt_authenticated_client_p.post('/api/receitas/', data=json.dumps(
        payload_receita_com_motivos_estorno_e_sem_outros_motivos), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert result['motivos_estorno'] == [motivo_estorno_01.id, motivo_estorno_02.id]
    assert result['outros_motivos_estorno'] == ""


def test_post_receita_sem_motivos_estorno_e_com_outros_motivos_estorno(
    payload_receita_sem_motivos_estorno_e_com_outros_motivos,
    jwt_authenticated_client_p,
):

    response = jwt_authenticated_client_p.post('/api/receitas/', data=json.dumps(
        payload_receita_sem_motivos_estorno_e_com_outros_motivos), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert result['motivos_estorno'] == []
    assert result['outros_motivos_estorno'] == "Outros motivos estorno"


def test_post_receita_sem_motivos_estorno_e_sem_outros_motivos_estorno(
    payload_receita_sem_motivos_estorno_e_sem_outros_motivos,
    jwt_authenticated_client_p,
):

    response = jwt_authenticated_client_p.post('/api/receitas/', data=json.dumps(
        payload_receita_sem_motivos_estorno_e_sem_outros_motivos), content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        "detail": "Para salvar um crédito do tipo estorno, é necessário informar o campo 'motivos_estorno' ou 'outros_motivos_estorno'"
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado


# put

def test_put_receita_com_motivos_estorno_e_outros_motivos_estorno(
    payload_receita_com_motivos_estorno_e_outros_motivos,
    jwt_authenticated_client_p,
    motivo_estorno_01,
    motivo_estorno_02,
    receita_estorno_motivos,
    associacao
):

    response = jwt_authenticated_client_p.put(f'/api/receitas/{receita_estorno_motivos.uuid}/?associacao_uuid={associacao.uuid}', data=json.dumps(
        payload_receita_com_motivos_estorno_e_outros_motivos), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    assert result['motivos_estorno'] == [motivo_estorno_01.id, motivo_estorno_02.id]
    assert result['outros_motivos_estorno'] == "Outros motivos estorno"


def test_put_receita_com_motivos_estorno_e_sem_outros_motivos_estorno(
    payload_receita_com_motivos_estorno_e_sem_outros_motivos,
    jwt_authenticated_client_p,
    motivo_estorno_01,
    motivo_estorno_02,
    receita_estorno_motivos,
    associacao
):

    response = jwt_authenticated_client_p.put(
        f'/api/receitas/{receita_estorno_motivos.uuid}/?associacao_uuid={associacao.uuid}', data=json.dumps(
            payload_receita_com_motivos_estorno_e_sem_outros_motivos), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    assert result['motivos_estorno'] == [motivo_estorno_01.id, motivo_estorno_02.id]
    assert result['outros_motivos_estorno'] == ""


def test_put_receita_sem_motivos_estorno_e_com_outros_motivos_estorno(
    payload_receita_sem_motivos_estorno_e_com_outros_motivos,
    jwt_authenticated_client_p,
    motivo_estorno_01,
    motivo_estorno_02,
    receita_estorno_motivos,
    associacao
):
    response = jwt_authenticated_client_p.put(
        f'/api/receitas/{receita_estorno_motivos.uuid}/?associacao_uuid={associacao.uuid}', data=json.dumps(
            payload_receita_sem_motivos_estorno_e_com_outros_motivos), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    assert result['motivos_estorno'] == []
    assert result['outros_motivos_estorno'] == "Outros motivos estorno"


def test_put_receita_sem_motivos_estorno_e_sem_outros_motivos_estorno(
    payload_receita_sem_motivos_estorno_e_sem_outros_motivos,
    jwt_authenticated_client_p,
    receita_estorno_motivos,
    associacao
):
    response = jwt_authenticated_client_p.put(
        f'/api/receitas/{receita_estorno_motivos.uuid}/?associacao_uuid={associacao.uuid}', data=json.dumps(
            payload_receita_sem_motivos_estorno_e_sem_outros_motivos), content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        "detail": "Para salvar um crédito do tipo estorno, é necessário informar o campo 'motivos_estorno' ou 'outros_motivos_estorno'"
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado
