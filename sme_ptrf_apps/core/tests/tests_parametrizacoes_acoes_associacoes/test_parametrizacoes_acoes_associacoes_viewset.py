import datetime

import pytest
from model_bakery import baker
from rest_framework import status

from sme_ptrf_apps.core.models import Recurso

pytestmark = pytest.mark.django_db


def test_list_parametrizacoes_acoes_associacoes(jwt_authenticated_client_a, acao_associacao):
    response = jwt_authenticated_client_a.get(
        '/api/parametrizacoes-acoes-associacoes/', content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(acao_associacao.uuid) in uuids


def test_list_filtro_nome(jwt_authenticated_client_a, acao_associacao):
    nome = acao_associacao.associacao.nome
    response = jwt_authenticated_client_a.get(
        f'/api/parametrizacoes-acoes-associacoes/?nome={nome}', content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(acao_associacao.uuid) in uuids


def test_list_filtro_nome_sem_resultado(jwt_authenticated_client_a, acao_associacao):
    response = jwt_authenticated_client_a.get(
        '/api/parametrizacoes-acoes-associacoes/?nome=NomeQueNaoExiste', content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result['results'] == []


@pytest.fixture
def associacao_encerrada(unidade, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Associacao Encerrada',
        unidade=unidade,
        periodo_inicial=periodo_anterior,
        data_de_encerramento=datetime.date(2020, 1, 1),
    )


@pytest.fixture
def acao_associacao_encerrada(associacao_encerrada, acao):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao_encerrada,
        acao=acao,
    )


def test_list_filtro_informacoes_nao_encerradas(
    jwt_authenticated_client_a, acao_associacao, acao_associacao_encerrada,
):
    response = jwt_authenticated_client_a.get(
        '/api/parametrizacoes-acoes-associacoes/?filtro_informacoes=NAO_ENCERRADAS',
        content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(acao_associacao.uuid) in uuids
    assert str(acao_associacao_encerrada.uuid) not in uuids


def test_list_filtro_informacoes_encerradas(
    jwt_authenticated_client_a, acao_associacao, acao_associacao_encerrada,
):
    response = jwt_authenticated_client_a.get(
        '/api/parametrizacoes-acoes-associacoes/?filtro_informacoes=ENCERRADAS',
        content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(acao_associacao_encerrada.uuid) in uuids
    assert str(acao_associacao.uuid) not in uuids


def test_list_filtro_informacoes_encerradas_e_nao_encerradas(
    jwt_authenticated_client_a, acao_associacao, acao_associacao_encerrada,
):
    response = jwt_authenticated_client_a.get(
        '/api/parametrizacoes-acoes-associacoes/?filtro_informacoes=ENCERRADAS,NAO_ENCERRADAS',
        content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(acao_associacao.uuid) in uuids
    assert str(acao_associacao_encerrada.uuid) in uuids


@pytest.fixture
def recurso_ptrf():
    return baker.make(
        'Recurso',
        nome_exibicao='PTRF',
        cor=Recurso.CorChoices.AZUL,
    )


def test_list_filtro_recurso_uuid(jwt_authenticated_client_a, acao_associacao, recurso_ptrf):
    acao_associacao.acao.recurso = recurso_ptrf
    acao_associacao.acao.save()

    response = jwt_authenticated_client_a.get(
        f'/api/parametrizacoes-acoes-associacoes/?recurso_uuid={recurso_ptrf.uuid}',
        content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(acao_associacao.uuid) in uuids


def test_list_filtro_recurso_uuid_nao_encontrado(jwt_authenticated_client_a, acao_associacao, recurso_ptrf):
    acao_associacao.acao.recurso = recurso_ptrf
    acao_associacao.acao.save()

    response = jwt_authenticated_client_a.get(
        '/api/parametrizacoes-acoes-associacoes/?recurso_uuid=00000000-0000-0000-0000-000000000000',
        content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(acao_associacao.uuid) not in uuids
