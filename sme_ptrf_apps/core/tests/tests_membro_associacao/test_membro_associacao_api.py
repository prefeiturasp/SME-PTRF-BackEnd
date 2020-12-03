import json

import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework import status

from sme_ptrf_apps.core.models import MembroAssociacao

from sme_ptrf_apps.core.choices import MembroEnum, RepresentacaoCargo

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_get_membros_associacoes(
        jwt_authenticated_client_a,
        associacao,
        membro_associacao):

    response = jwt_authenticated_client_a.get(
        f'/api/membros-associacao/?associacao_uuid={associacao.uuid}', content_type='application/json')
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
            'usuario': None,
            'email': membro_associacao.email,
            'cpf': membro_associacao.cpf
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_get_membro_associacao(
        jwt_authenticated_client_a,
        associacao,
        membro_associacao):

    response = jwt_authenticated_client_a.get(
        f'/api/membros-associacao/{membro_associacao.uuid}/?associacao_uuid={associacao.uuid}', content_type='application/json')
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
        'email': membro_associacao.email,
        'cpf': membro_associacao.cpf,
        'usuario': None,
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_criar_membro_associacao_servidor(jwt_authenticated_client_a, associacao, payload_membro_servidor):
    response = jwt_authenticated_client_a.post(
        '/api/membros-associacao/', data=json.dumps(payload_membro_servidor), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert MembroAssociacao.objects.filter(uuid=result['uuid']).exists()


def test_criar_membro_associacao_servidor_com_usuario(jwt_authenticated_client_a, associacao, payload_membro_servidor):
    usuario = User.objects.filter(username='7210418').first()
    payload_membro_servidor['usuario'] = usuario.id

    response = jwt_authenticated_client_a.post(
        '/api/membros-associacao/', data=json.dumps(payload_membro_servidor), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert MembroAssociacao.objects.filter(uuid=result['uuid']).exists()
    assert MembroAssociacao.objects.filter(uuid=result['uuid']).first().usuario
    assert MembroAssociacao.objects.filter(uuid=result['uuid']).first().usuario.username == "7210418"


def test_criar_membro_associacao_servidor_com_usuario_none(jwt_authenticated_client_a, associacao, payload_membro_servidor):
    usuario = User.objects.filter(username='7210418').first()
    payload_membro_servidor['usuario'] = None

    response = jwt_authenticated_client_a.post(
        '/api/membros-associacao/', data=json.dumps(payload_membro_servidor), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert MembroAssociacao.objects.filter(uuid=result['uuid']).exists()
    assert not MembroAssociacao.objects.filter(uuid=result['uuid']).first().usuario


def test_criar_membro_associacao_estudante(jwt_authenticated_client_a, associacao, payload_membro_estudante):
    response = jwt_authenticated_client_a.post(
        '/api/membros-associacao/', data=json.dumps(payload_membro_estudante), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert MembroAssociacao.objects.filter(uuid=result['uuid']).exists()


def test_criar_membro_associacao_pai_responsavel(jwt_authenticated_client_a, associacao, payload_membro_pai_responsavel):
    response = jwt_authenticated_client_a.post(
        '/api/membros-associacao/', data=json.dumps(payload_membro_pai_responsavel), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert MembroAssociacao.objects.filter(uuid=result['uuid']).exists()


def test_atualizar_membro_associacao_servidor(jwt_authenticated_client_a, associacao, membro_associacao, payload_membro_servidor):
    nome_novo = "Gabriel Nóbrega"
    payload_membro_servidor['nome'] = nome_novo
    response = jwt_authenticated_client_a.put(
        f'/api/membros-associacao/{membro_associacao.uuid}/?associacao_uuid={associacao.uuid}', data=json.dumps(payload_membro_servidor), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    assert MembroAssociacao.objects.filter(uuid=result['uuid']).exists()

    membro = MembroAssociacao.objects.filter(uuid=result['uuid']).get()

    assert membro.nome == nome_novo


@pytest.fixture
def usuario_membro(unidade):
    senha = 'Sgp1981'
    login = '7212009'
    email = 'sme2009@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.save()
    return user


@pytest.fixture
def membro_associacao_2(associacao, usuario_membro):
    return baker.make(
        'MembroAssociacao',
        nome='Arthur Nobrega',
        associacao=associacao,
        cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.value,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.SERVIDOR.value,
        codigo_identificacao='567432',
        email='ollyverottoboni@gmail.com',
        usuario=usuario_membro
    )


def test_atualizar_membro_associacao_servidor_com_usuario(jwt_authenticated_client_a, associacao, usuario_membro, membro_associacao_2, payload_membro_servidor):
    usuario = User.objects.filter(username='7210418').first()
    payload_membro_servidor['usuario'] = usuario.id
    assert membro_associacao_2.usuario == usuario_membro
    response = jwt_authenticated_client_a.put(
        f'/api/membros-associacao/{membro_associacao_2.uuid}/?associacao_uuid={associacao.uuid}', data=json.dumps(payload_membro_servidor), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    assert MembroAssociacao.objects.filter(uuid=result['uuid']).exists()

    membro = MembroAssociacao.objects.filter(uuid=result['uuid']).get()

    assert membro.usuario == usuario


def test_atualizar_membro_associacao_servidor_com_usuario_none(jwt_authenticated_client_a, associacao, usuario_membro, membro_associacao_2, payload_membro_servidor):
    payload_membro_servidor['usuario'] = None
    assert membro_associacao_2.usuario == usuario_membro
    response = jwt_authenticated_client_a.put(
        f'/api/membros-associacao/{membro_associacao_2.uuid}/?associacao_uuid={associacao.uuid}', data=json.dumps(payload_membro_servidor), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    assert MembroAssociacao.objects.filter(uuid=result['uuid']).exists()

    membro = MembroAssociacao.objects.filter(uuid=result['uuid']).get()

    assert not membro.usuario


def test_deletar_membro_associacao(jwt_authenticated_client_a, associacao, membro_associacao):
    assert MembroAssociacao.objects.filter(uuid=membro_associacao.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/membros-associacao/{membro_associacao.uuid}/?associacao_uuid={associacao.uuid}', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not MembroAssociacao.objects.filter(uuid=membro_associacao.uuid).exists()
