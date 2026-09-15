import pytest
from model_bakery import baker
from rest_framework import status

from sme_ptrf_apps.core.models import Recurso

pytestmark = pytest.mark.django_db


def test_list_parametrizacoes_associacoes(jwt_authenticated_client_a, associacao):
    response = jwt_authenticated_client_a.get(
        '/api/parametrizacoes-associacoes/', content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(associacao.uuid) in uuids


def test_list_filtro_recurso_uuid(jwt_authenticated_client_a, associacao):
    recurso_legado = Recurso.objects.get(legado=True)

    response = jwt_authenticated_client_a.get(
        f'/api/parametrizacoes-associacoes/?recurso_uuid={recurso_legado.uuid}',
        content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(associacao.uuid) in uuids


def test_list_filtro_recurso_uuid_sem_vinculo(jwt_authenticated_client_a, associacao):
    outro_recurso = baker.make(
        'Recurso',
        nome_exibicao='Outro Recurso',
        cor=Recurso.CorChoices.VERDE,
    )

    response = jwt_authenticated_client_a.get(
        f'/api/parametrizacoes-associacoes/?recurso_uuid={outro_recurso.uuid}',
        content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(associacao.uuid) not in uuids


def test_list_filtro_recurso_uuid_nao_encontrado(jwt_authenticated_client_a, associacao):
    response = jwt_authenticated_client_a.get(
        '/api/parametrizacoes-associacoes/?recurso_uuid=00000000-0000-0000-0000-000000000000',
        content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(associacao.uuid) in uuids


def test_list_filtro_recurso_uuid_vazio(jwt_authenticated_client_a, associacao):
    response = jwt_authenticated_client_a.get(
        '/api/parametrizacoes-associacoes/?recurso_uuid=', content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(associacao.uuid) in uuids


def test_list_filtro_unidade_dre_uuid(jwt_authenticated_client_a, associacao, dre):
    response = jwt_authenticated_client_a.get(
        f'/api/parametrizacoes-associacoes/?unidade__dre__uuid={dre.uuid}',
        content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(associacao.uuid) in uuids


def test_list_filtro_unidade_dre_uuid_vazio(jwt_authenticated_client_a, associacao):
    response = jwt_authenticated_client_a.get(
        '/api/parametrizacoes-associacoes/?unidade__dre__uuid=', content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(associacao.uuid) in uuids


def test_list_filtro_nome(jwt_authenticated_client_a, associacao):
    response = jwt_authenticated_client_a.get(
        f'/api/parametrizacoes-associacoes/?nome={associacao.nome}',
        content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(associacao.uuid) in uuids


def test_list_filtro_nome_sem_resultado(jwt_authenticated_client_a, associacao):
    response = jwt_authenticated_client_a.get(
        '/api/parametrizacoes-associacoes/?nome=NomeQueNaoExiste', content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result['results'] == []


def test_list_filtro_informacoes_nao_encerradas(
    jwt_authenticated_client_a, associacao, associacao_com_data_de_encerramento,
):
    response = jwt_authenticated_client_a.get(
        '/api/parametrizacoes-associacoes/?filtro_informacoes=NAO_ENCERRADAS',
        content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(associacao.uuid) in uuids
    assert str(associacao_com_data_de_encerramento.uuid) not in uuids


def test_list_filtro_informacoes_encerradas(
    jwt_authenticated_client_a, associacao, associacao_com_data_de_encerramento,
):
    response = jwt_authenticated_client_a.get(
        '/api/parametrizacoes-associacoes/?filtro_informacoes=ENCERRADAS',
        content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(associacao_com_data_de_encerramento.uuid) in uuids
    assert str(associacao.uuid) not in uuids


def test_list_filtro_informacoes_encerradas_e_nao_encerradas(
    jwt_authenticated_client_a, associacao, associacao_com_data_de_encerramento,
):
    response = jwt_authenticated_client_a.get(
        '/api/parametrizacoes-associacoes/?filtro_informacoes=ENCERRADAS,NAO_ENCERRADAS',
        content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in result['results']]
    assert str(associacao.uuid) in uuids
    assert str(associacao_com_data_de_encerramento.uuid) in uuids
