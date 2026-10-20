import json

import pytest
from rest_framework import status

from sme_ptrf_apps.core.choices import MembroEnum

pytestmark = pytest.mark.django_db


def test_get_membros_cargos(jwt_authenticated_client_a, associacao, membro_associacao):
    response = jwt_authenticated_client_a.get(
        f'/api/membros-associacao/membros-cargos/?associacao_uuid={associacao.uuid}',
        content_type='application/json',
    )
    result = json.loads(response.content)

    esperado = [
        {
            'uuid': str(membro_associacao.uuid),
            'nome': membro_associacao.nome,
            'cargo_associacao_key': membro_associacao.cargo_associacao,
            'cargo_associacao_value': membro_associacao.get_cargo_associacao_display(),
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_get_membros_cargos_sem_membros(jwt_authenticated_client_a, associacao):
    response = jwt_authenticated_client_a.get(
        f'/api/membros-associacao/membros-cargos/?associacao_uuid={associacao.uuid}',
        content_type='application/json',
    )
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == []


def test_get_membros_cargos_sem_associacao_uuid(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(
        '/api/membros-associacao/membros-cargos/', content_type='application/json',
    )
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'parametros_requerido'


def test_get_cargos_diretoria_executiva(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(
        '/api/membros-associacao/cargos-diretoria-executiva/', content_type='application/json',
    )
    result = json.loads(response.content)

    esperado = [
        {'id': choice[0], 'nome': choice[1]}
        for choice in MembroEnum.diretoria_executiva_choices()
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
