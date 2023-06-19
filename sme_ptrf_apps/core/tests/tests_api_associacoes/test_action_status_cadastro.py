import json
import pytest

from freezegun import freeze_time
from rest_framework import status

pytestmark = pytest.mark.django_db

@freeze_time('2020-07-10 10:20:00')
def test_status_cadastro_somente_pendencia_cadastro(
    jwt_authenticated_client_a,
    associacao_cadastro_incompleto,
    membro_associacao_cadastro_incompleto_001,
    membro_associacao_cadastro_incompleto_002,
    membro_associacao_cadastro_incompleto_003,
    membro_associacao_cadastro_incompleto_004,
    membro_associacao_cadastro_incompleto_005,
    membro_associacao_cadastro_incompleto_006,
    membro_associacao_cadastro_incompleto_007,
    membro_associacao_cadastro_incompleto_008,
    membro_associacao_cadastro_incompleto_009,
    membro_associacao_cadastro_incompleto_010,
    membro_associacao_cadastro_incompleto_011,
    membro_associacao_cadastro_incompleto_012,
    membro_associacao_cadastro_incompleto_013,
    membro_associacao_cadastro_incompleto_014,
):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao_cadastro_incompleto.uuid}/status-cadastro/',
                          content_type='application/json')
    result = json.loads(response.content)

    status_cadastro_esperado = {
        'pendencia_cadastro': True,
        'pendencia_contas': False,
        'pendencia_membros': False
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == status_cadastro_esperado

@freeze_time('2020-07-10 10:20:00')
def test_status_cadastro_somente_pendencia_contas(
    jwt_authenticated_client_a,
    membro_associacao_001,
    membro_associacao_002,
    membro_associacao_003,
    membro_associacao_004,
    membro_associacao_005,
    membro_associacao_006,
    membro_associacao_007,
    membro_associacao_008,
    membro_associacao_009,
    membro_associacao_010,
    membro_associacao_011,
    membro_associacao_012,
    membro_associacao_013,
    membro_associacao_014,
    conta_associacao_incompleta_002,
):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{conta_associacao_incompleta_002.associacao.uuid}/status-cadastro/',
                          content_type='application/json')
    result = json.loads(response.content)

    status_cadastro_esperado = {
        'pendencia_cadastro': False,
        'pendencia_contas': True,
        'pendencia_membros': False
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == status_cadastro_esperado

@freeze_time('2020-07-10 10:20:00')
def test_status_cadastro_somente_pendencia_membros(
    jwt_authenticated_client_a,
    associacao,
):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/status-cadastro/',
                          content_type='application/json')
    result = json.loads(response.content)

    status_cadastro_esperado = {
        'pendencia_cadastro': False,
        'pendencia_contas': False,
        'pendencia_membros': True
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == status_cadastro_esperado

@freeze_time('2020-07-10 10:20:00')
def test_status_cadastro_todas_as_pendencias(
    jwt_authenticated_client_a,
    conta_associacao_incompleta,
):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{conta_associacao_incompleta.associacao.uuid}/status-cadastro/',
                          content_type='application/json')
    result = json.loads(response.content)

    status_cadastro_esperado = {
        'pendencia_cadastro': True,
        'pendencia_contas': True,
        'pendencia_membros': True
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == status_cadastro_esperado

