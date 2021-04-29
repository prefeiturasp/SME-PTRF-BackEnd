import json
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from rest_framework import status

pytestmark = pytest.mark.django_db

def test_consulta_grupos(
        jwt_authenticated_client_u2,
        usuario_2,
        visao_ue,
        visao_dre,
        visao_sme,
        permissao1,
        permissao2,
        grupo_1,
        grupo_2,
        grupo_3):

    response = jwt_authenticated_client_u2.get("/api/usuarios/grupos/?visao=DRE", content_type='application/json')
    result = response.json()
    esperado = [
        {
            "id": str(grupo_2.id),
            "nome": grupo_2.name,
            "descricao": grupo_2.descricao
        },
        {
            "id": str(grupo_3.id),
            "nome": grupo_3.name,
            "descricao": grupo_3.descricao
        }]

    assert result == esperado


def test_lista_usuarios(
        jwt_authenticated_client_u,
        usuario_para_teste,
        usuario_3,
        visao_ue,
        visao_dre,
        visao_sme,
        permissao1,
        permissao2,
        grupo_1,
        grupo_2):

    response = jwt_authenticated_client_u.get("/api/usuarios/?visao=DRE", content_type='application/json')
    result = response.json()
    esperado = [
        {
            'id': usuario_3.id,
            'username': usuario_3.username,
            'email': usuario_3.email,
            'name': usuario_3.name,
            'url': f'http://testserver/api/esqueci-minha-senha/{usuario_3.username}/',
            'e_servidor': usuario_3.e_servidor,
            'groups': [{'id': grupo_2.id, 'name': grupo_2.name, 'descricao': grupo_2.descricao}]
        }
    ]
    assert result == esperado


def test_filtro_por_grupo_lista_usuarios(
        jwt_authenticated_client_u2,
        usuario_2,
        usuario_3,
        visao_ue,
        visao_dre,
        visao_sme,
        permissao1,
        permissao2,
        grupo_1,
        grupo_2):

    response = jwt_authenticated_client_u2.get(
        f"/api/usuarios/?visao=DRE&groups__id={grupo_2.id}", content_type='application/json')
    result = response.json()
    esperado = [
        {
            'id': usuario_3.id,
            'username': '7218198',
            'email': 'sme8198@amcom.com.br',
            'name': 'Arthur Marques',
            'url': 'http://testserver/api/esqueci-minha-senha/7218198/',
            'e_servidor': usuario_3.e_servidor,
            'groups': [
                {
                   'id': grupo_2.id,
                   'name': 'grupo2',
                   'descricao': 'Descrição grupo 2'
                }
            ]
        }
    ]
    assert result == esperado


def test_filtro_por_nome_lista_usuarios(
        jwt_authenticated_client_u2,
        usuario_2,
        usuario_3,
        visao_ue,
        visao_dre,
        visao_sme,
        permissao1,
        permissao2,
        grupo_1,
        grupo_2):

    response = jwt_authenticated_client_u2.get(f"/api/usuarios/?visao=DRE&search=Arth", content_type='application/json')
    result = response.json()
    esperado = [
        {'id': usuario_3.id,
         'username': '7218198',
         'email': 'sme8198@amcom.com.br',
         'name': 'Arthur Marques',
         'url': 'http://testserver/api/esqueci-minha-senha/7218198/',
         'e_servidor': usuario_3.e_servidor,
         'groups': [
             {
                'id': grupo_2.id,
                'name': 'grupo2',
                'descricao': 'Descrição grupo 2'}]
         }
    ]
    assert result == esperado


def test_criar_usuario_servidor(
        jwt_authenticated_client_u,
        grupo_1,
        visao_dre):

    payload = {
        'e_servidor': True,
        'username': "9876543",
        'name': "Lukaku Silva",
        'email': 'lukaku@gmail.com',
        'visao': "DRE",
        'groups': [
            grupo_1.id,
        ]
    }
    response = jwt_authenticated_client_u.post(
        "/api/usuarios/", data=json.dumps(payload), content_type='application/json')
    result = response.json()

    esperado = {
        'username': '9876543',
        'email': 'lukaku@gmail.com',
        'name': 'Lukaku Silva',
        'e_servidor': True,
        'groups': [grupo_1.id,]
    }
    User = get_user_model()
    u = User.objects.filter(username='9876543').first()

    assert len(u.visoes.all()) > 0
    assert response.status_code == status.HTTP_201_CREATED
    assert result == esperado


def test_criar_usuario_servidor_sem_email_e_sem_nome(
        jwt_authenticated_client_u,
        grupo_1,
        visao_dre):

    payload = {
        'e_servidor': True,
        'username': "9876543",
        'name': "",
        'email': "",
        'visao': "DRE",
        'groups': [
            grupo_1.id,
        ]
    }
    response = jwt_authenticated_client_u.post(
        "/api/usuarios/", data=json.dumps(payload), content_type='application/json')
    result = response.json()
    esperado = {
        'username': '9876543',
        'email': '',
        'name': '',
        'e_servidor': True,
        'groups': [grupo_1.id,]
    }
    User = get_user_model()
    u = User.objects.filter(username='9876543').first()

    assert len(u.visoes.all()) > 0
    assert response.status_code == status.HTTP_201_CREATED
    assert result == esperado


def test_atualizar_usuario_servidor(
        jwt_authenticated_client_u,
        usuario_3,
        usuario_2,
        visao_ue,
        visao_dre,
        visao_sme,
        grupo_1,
        grupo_2):

    assert not usuario_2.visoes.filter(nome='UE').first()

    payload = {
        'e_servidor': True,
        'username': usuario_2.username,
        'name': usuario_2.name,
        'email': 'novoEmail@gmail.com',
        'visao': "UE",
        'groups': [
            grupo_1.id
        ]
    }

    response = jwt_authenticated_client_u.put(
        f"/api/usuarios/{usuario_2.id}/", data=json.dumps(payload), content_type='application/json')
    result = response.json()

    esperado = {
        'username': usuario_2.username,
        'email': 'novoEmail@gmail.com',
        'name': usuario_2.name,
        'e_servidor': True,
        'groups': [grupo_1.id]
    }

    assert usuario_2.visoes.filter(nome='UE').first()
    assert result == esperado


def test_deletar_usuario_servidor(
        jwt_authenticated_client_u,
        usuario_3
):

    from django.contrib.auth import get_user_model

    User = get_user_model()
    assert User.objects.filter(id=usuario_3.id).exists()

    response = jwt_authenticated_client_u.delete(
        f"/api/usuarios/{usuario_3.id}/", content_type='application/json')
    assert not User.objects.filter(id=usuario_3.id).exists()


def test_consulta_informacao_usuario(jwt_authenticated_client_u):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.informacao_usuario_sgp'
    with patch(path) as mock_get:
        data = {
            'cpf': '12808888813',
            'nome': 'LUCIMARA CARDOSO RODRIGUES',
            'codigoRf': '7210418',
            'email': 'tutu@gmail.com',
            'emailValido': True
        }

        mock_get.return_value = data

        username = '7210418'
        response = jwt_authenticated_client_u.get(f'/api/usuarios/consultar/?username={7210418}')
        result = json.loads(response.content)
        assert response.status_code == status.HTTP_200_OK
        assert result == data


def test_consulta_informacao_usuario_sem_username(jwt_authenticated_client_u):
    response = jwt_authenticated_client_u.get(f'/api/usuarios/consultar/?username=')
    result = json.loads(response.content)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == "Parâmetro username obrigatório."


def test_lista_usuarios_por_unidade(
        jwt_authenticated_client_u,
        usuario_para_teste,
        usuario_2,
        usuario_3,
        associacao,
        grupo_1,
        grupo_2):

    response = jwt_authenticated_client_u.get(f"/api/usuarios/?associacao_uuid={associacao.uuid}", content_type='application/json')
    result = response.json()
    esperado = [
        {
            'id': usuario_3.id,
            'name': 'Arthur Marques',
            'e_servidor': True,
            'url': 'http://testserver/api/esqueci-minha-senha/7218198/',
            'username': '7218198',
            'email': 'sme8198@amcom.com.br',
            'groups': [
                {
                    'descricao': 'Descrição grupo 2',
                    'id': grupo_2.id,
                    'name': 'grupo2'
                }],
        },
        {
            'id': usuario_para_teste.id,
            'name': 'LUCIA HELENA',
            'e_servidor': False,
            'url': 'http://testserver/api/esqueci-minha-senha/7210418/',
            'username': '7210418',
            'email': 'luh@gmail.com',
            'groups': [
                {
                    'descricao': 'Descrição grupo 1',
                    'id': grupo_1.id,
                    'name': 'grupo1'
                }],
        }

    ]
    print(result)
    assert result == esperado
