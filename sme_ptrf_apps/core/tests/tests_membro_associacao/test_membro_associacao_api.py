import json

import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import MembroAssociacao

pytestmark = pytest.mark.django_db


def test_get_membros_associacoes(
        jwt_authenticated_client,
        associacao,
        membro_associacao):

    response = jwt_authenticated_client.get('/api/membros-associacao/', content_type='application/json')
    result = json.loads(response.content)

    esperado = [
        {
            'id': membro_associacao.id,
            'associacao':
            {
                'id': associacao.id,
                'nome': associacao.nome
            },
            'criado_em': membro_associacao.criado_em.isoformat("T"),
            'alterado_em': membro_associacao.alterado_em.isoformat("T"),
            'uuid': str(membro_associacao.uuid),
            'nome': membro_associacao.nome,
            'cargo_associacao': membro_associacao.cargo_associacao,
            'cargo_educacao': membro_associacao.cargo_educacao,
            'representacao': membro_associacao.representacao,
            'codigo_identificacao': membro_associacao.codigo_identificacao,
            'email': membro_associacao.email
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_get_membro_associacao(
        jwt_authenticated_client,
        associacao,
        membro_associacao):

    response = jwt_authenticated_client.get(
        f'/api/membros-associacao/{membro_associacao.uuid}/', content_type='application/json')
    result = json.loads(response.content)
    esperado = {
        'id': membro_associacao.id,
        'associacao':
            {
                'id': associacao.id,
                'nome': associacao.nome
            },
        'criado_em': membro_associacao.criado_em.isoformat("T"),
        'alterado_em': membro_associacao.alterado_em.isoformat("T"),
        'uuid': str(membro_associacao.uuid),
        'nome': membro_associacao.nome,
        'cargo_associacao': membro_associacao.cargo_associacao,
        'cargo_educacao': membro_associacao.cargo_educacao,
        'representacao': membro_associacao.representacao,
        'codigo_identificacao': membro_associacao.codigo_identificacao,
        'email': membro_associacao.email
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_criar_membro_associacao_servidor(jwt_authenticated_client, associacao, payload_membro_servidor):
    response = jwt_authenticated_client.post(
        '/api/membros-associacao/', data=json.dumps(payload_membro_servidor), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert MembroAssociacao.objects.filter(uuid=result['uuid']).exists()


def test_criar_membro_associacao_estudante(jwt_authenticated_client, associacao, payload_membro_estudante):
    response = jwt_authenticated_client.post(
        '/api/membros-associacao/', data=json.dumps(payload_membro_estudante), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert MembroAssociacao.objects.filter(uuid=result['uuid']).exists()


def test_criar_membro_associacao_pai_responsavel(jwt_authenticated_client, associacao, payload_membro_pai_responsavel):
    response = jwt_authenticated_client.post(
        '/api/membros-associacao/', data=json.dumps(payload_membro_pai_responsavel), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert MembroAssociacao.objects.filter(uuid=result['uuid']).exists()


def test_atualizar_membro_associacao_servidor(jwt_authenticated_client, associacao, membro_associacao, payload_membro_servidor):
    nome_novo = "Gabriel Nóbrega"
    payload_membro_servidor['nome'] = nome_novo
    response = jwt_authenticated_client.put(
        f'/api/membros-associacao/{membro_associacao.uuid}/', data=json.dumps(payload_membro_servidor), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    assert MembroAssociacao.objects.filter(uuid=result['uuid']).exists()

    membro = MembroAssociacao.objects.filter(uuid=result['uuid']).get()

    assert membro.nome == nome_novo


def test_deletar_membro_associacao(jwt_authenticated_client, membro_associacao):
    assert MembroAssociacao.objects.filter(uuid=membro_associacao.uuid).exists()

    response = jwt_authenticated_client.delete(
        f'/api/membros-associacao/{membro_associacao.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not MembroAssociacao.objects.filter(uuid=membro_associacao.uuid).exists()
