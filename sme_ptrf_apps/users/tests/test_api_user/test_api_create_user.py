import json
import pytest

from django.contrib.auth import get_user_model

from unittest.mock import patch, call

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_criar_usuario_servidor_com_visao(
        jwt_authenticated_client_u,
        grupo_1,
        visao_ue,
        unidade_ue_271170,
):
    payload = {
        'e_servidor': True,
        'username': "9876543",
        'name': "Lukaku Silva",
        'email': 'lukaku@gmail.com',
        'visao': "UE",
        'groups': [
            grupo_1.id,
        ],
        'unidade': unidade_ue_271170.codigo_eol
    }

    api_usuario_core_sso_or_none = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.usuario_core_sso_or_none'
    api_cria_usuario_core_sso = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.cria_usuario_core_sso'
    api_atribuir_perfil_core_sso = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.atribuir_perfil_coresso'
    with patch(api_usuario_core_sso_or_none) as mock_usuario_core_sso_or_none:
        mock_usuario_core_sso_or_none.return_value = None
        with patch(api_cria_usuario_core_sso) as mock_cria_usuario_core_sso:
            with patch(api_atribuir_perfil_core_sso) as mock_atribuir_perfil_core_sso:
                response = jwt_authenticated_client_u.post("/api/usuarios/", data=json.dumps(payload), content_type='application/json')

    result = response.json()


    User = get_user_model()
    u = User.objects.filter(username='9876543').first()

    esperado = {
        'username': '9876543',
        'email': 'lukaku@gmail.com',
        'name': 'Lukaku Silva',
        'e_servidor': True,
        'groups': [grupo_1.id, ],
        'visoes': [visao_ue.id, ],
        'id': u.id
    }

    assert list(u.visoes.values_list('nome', flat=True)) == ["UE", ]
    assert list(u.unidades.values_list('codigo_eol', flat=True)) == [unidade_ue_271170.codigo_eol,]
    assert response.status_code == status.HTTP_201_CREATED
    assert result == esperado
    mock_usuario_core_sso_or_none.assert_called_once_with(login='9876543')
    mock_cria_usuario_core_sso.assert_called_once_with(
        e_servidor=True,
        email='lukaku@gmail.com',
        login='9876543',
        nome='Lukaku Silva'
    )
    mock_atribuir_perfil_core_sso.assert_called_once_with(login='9876543', visao='UE')


def test_criar_usuario_servidor_com_visoes(
        jwt_authenticated_client_u,
        grupo_1,
        visao_ue,
        unidade_ue_271170,
):
    payload = {
        'e_servidor': True,
        'username': "9876543",
        'name': "Lukaku Silva",
        'email': 'lukaku@gmail.com',
        'visoes': [visao_ue.id, ],
        'groups': [grupo_1.id, ],
        'unidade': unidade_ue_271170.codigo_eol
    }

    api_usuario_core_sso_or_none = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.usuario_core_sso_or_none'
    api_cria_usuario_core_sso = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.cria_usuario_core_sso'
    api_atribuir_perfil_core_sso = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.atribuir_perfil_coresso'
    with patch(api_usuario_core_sso_or_none) as mock_usuario_core_sso_or_none:
        mock_usuario_core_sso_or_none.return_value = None
        with patch(api_cria_usuario_core_sso) as mock_cria_usuario_core_sso:
            with patch(api_atribuir_perfil_core_sso) as mock_atribuir_perfil_core_sso:
                response = jwt_authenticated_client_u.post("/api/usuarios/", data=json.dumps(payload), content_type='application/json')

    result = response.json()

    User = get_user_model()
    u = User.objects.filter(username='9876543').first()

    esperado = {
        'username': '9876543',
        'email': 'lukaku@gmail.com',
        'name': 'Lukaku Silva',
        'e_servidor': True,
        'groups': [grupo_1.id, ],
        'visoes': [visao_ue.id, ],
        'id': u.id
    }

    assert list(u.visoes.values_list('nome', flat=True)) == ["UE", ]
    assert list(u.unidades.values_list('codigo_eol', flat=True)) == [unidade_ue_271170.codigo_eol,]
    assert response.status_code == status.HTTP_201_CREATED
    assert result == esperado
    mock_usuario_core_sso_or_none.assert_called_once_with(login='9876543')
    mock_cria_usuario_core_sso.assert_called_once_with(
        e_servidor=True,
        email='lukaku@gmail.com',
        login='9876543',
        nome='Lukaku Silva'
    )
    mock_atribuir_perfil_core_sso.assert_called_once_with(login='9876543', visao='UE')


def test_criar_usuario_servidor_sem_email_e_sem_nome(
        jwt_authenticated_client_u,
        grupo_1,
        visao_ue,
        unidade_ue_271170
):

    payload = {
        'e_servidor': True,
        'username': "9876543",
        'name': "",
        'email': "",
        'visao': "UE",
        'groups': [
            grupo_1.id,
        ],
        'unidade': unidade_ue_271170.codigo_eol
    }
    response = jwt_authenticated_client_u.post(
        "/api/usuarios/", data=json.dumps(payload), content_type='application/json')
    result = response.json()

    User = get_user_model()
    u = User.objects.filter(username='9876543').first()

    esperado = {
        'username': '9876543',
        'email': '',
        'name': '',
        'e_servidor': True,
        'groups': [grupo_1.id, ],
        'visoes': [visao_ue.id, ],
        'id': u.id
    }

    assert list(u.visoes.values_list('nome', flat=True)) == ["UE", ]
    assert list(u.unidades.values_list('codigo_eol', flat=True)) == [unidade_ue_271170.codigo_eol, ]
    assert response.status_code == status.HTTP_201_CREATED
    assert result == esperado


def test_criar_usuario_servidor_visao_sme(
        jwt_authenticated_client_u,
        grupo_1,
        visao_ue,
        visao_sme,
        unidade_ue_271170,
):
    payload = {
        'e_servidor': True,
        'username': "9876543",
        'name': "Lukaku Silva",
        'email': 'lukaku@gmail.com',
        'visoes': [visao_ue.id, visao_sme.id],
        'groups': [grupo_1.id, ],
        'unidade': None
    }

    api_usuario_core_sso_or_none = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.usuario_core_sso_or_none'
    api_cria_usuario_core_sso = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.cria_usuario_core_sso'
    api_atribuir_perfil_core_sso = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.atribuir_perfil_coresso'
    with patch(api_usuario_core_sso_or_none) as mock_usuario_core_sso_or_none:
        mock_usuario_core_sso_or_none.return_value = None
        with patch(api_cria_usuario_core_sso) as mock_cria_usuario_core_sso:
            with patch(api_atribuir_perfil_core_sso) as mock_atribuir_perfil_core_sso:
                response = jwt_authenticated_client_u.post("/api/usuarios/", data=json.dumps(payload), content_type='application/json')

    result = response.json()

    User = get_user_model()
    u = User.objects.filter(username='9876543').first()

    esperado = {
        'username': '9876543',
        'email': 'lukaku@gmail.com',
        'name': 'Lukaku Silva',
        'e_servidor': True,
        'visoes': [visao_ue.id, visao_sme.id],
        'groups': [grupo_1.id, ],
        'id': u.id
    }

    # TODO Rever assert. A ordem das linhas variam de teste pra teste.
    # assert list(u.visoes.values_list('nome', flat=True)) == ["UE", "SME"]

    assert response.status_code == status.HTTP_201_CREATED
    assert result == esperado
    mock_usuario_core_sso_or_none.assert_called_once_with(login='9876543')
    mock_cria_usuario_core_sso.assert_called_once_with(
        e_servidor=True,
        email='lukaku@gmail.com',
        login='9876543',
        nome='Lukaku Silva'
    )
    mock_atribuir_perfil_core_sso.assert_has_calls([call(login='9876543', visao='UE'), call(login='9876543', visao='SME')])


def test_criar_usuario_servidor_com_visoes_sem_definir_unidade(
        jwt_authenticated_client_u,
        grupo_1,
        visao_ue,
        unidade_ue_271170,
):
    payload = {
        'e_servidor': True,
        'username': "9876543",
        'name': "Lukaku Silva",
        'email': 'lukaku@gmail.com',
        'visoes': [visao_ue.id, ],
        'groups': [grupo_1.id, ],
        'unidade': None
    }

    api_usuario_core_sso_or_none = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.usuario_core_sso_or_none'
    api_cria_usuario_core_sso = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.cria_usuario_core_sso'
    api_atribuir_perfil_core_sso = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.atribuir_perfil_coresso'
    with patch(api_usuario_core_sso_or_none) as mock_usuario_core_sso_or_none:
        mock_usuario_core_sso_or_none.return_value = None
        with patch(api_cria_usuario_core_sso) as mock_cria_usuario_core_sso:
            with patch(api_atribuir_perfil_core_sso) as mock_atribuir_perfil_core_sso:
                response = jwt_authenticated_client_u.post("/api/usuarios/", data=json.dumps(payload), content_type='application/json')

    result = response.json()

    User = get_user_model()
    u = User.objects.filter(username='9876543').first()

    esperado = {
        'username': '9876543',
        'email': 'lukaku@gmail.com',
        'name': 'Lukaku Silva',
        'e_servidor': True,
        'groups': [grupo_1.id, ],
        'visoes': [visao_ue.id, ],
        'id': u.id

    }

    assert list(u.visoes.values_list('nome', flat=True)) == ["UE", ]
    assert list(u.unidades.values_list('codigo_eol', flat=True)) == []
    assert response.status_code == status.HTTP_201_CREATED
    assert result == esperado
    mock_usuario_core_sso_or_none.assert_called_once_with(login='9876543')
    mock_cria_usuario_core_sso.assert_called_once_with(
        e_servidor=True,
        email='lukaku@gmail.com',
        login='9876543',
        nome='Lukaku Silva'
    )
    mock_atribuir_perfil_core_sso.assert_called_once_with(login='9876543', visao='UE')

