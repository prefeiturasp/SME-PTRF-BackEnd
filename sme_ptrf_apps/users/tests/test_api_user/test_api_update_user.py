import json
import pytest

from unittest.mock import patch, call
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_atualizar_usuario_servidor_com_visao(
        jwt_authenticated_client_u,
        usuario_3,
        usuario_2,
        visao_ue,
        visao_dre,
        visao_sme,
        grupo_1,
        grupo_2,
        unidade_ue_271170,
        unidade_diferente,
        dre
):
    assert not usuario_2.unidades.filter(codigo_eol='271170').first(), "Não deveria estar vinculado à unidade 271170 antes do teste."
    assert not usuario_2.visoes.filter(nome='UE').first(), "Não deveria estar vinculado à UE antes do teste."

    payload = {
        'e_servidor': True,
        'username': usuario_2.username,
        'name': usuario_2.name,
        'email': 'novoEmail@gmail.com',
        'visao': "UE",
        'unidade': "271170",
        'groups': [grupo_1.id]
    }

    api_usuario_core_sso_or_none = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.usuario_core_sso_or_none'
    api_cria_usuario_core_sso = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.cria_usuario_core_sso'
    api_atribuir_perfil_core_sso = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.atribuir_perfil_coresso'
    with patch(api_usuario_core_sso_or_none) as mock_usuario_core_sso_or_none:
        mock_usuario_core_sso_or_none.return_value = None
        with patch(api_cria_usuario_core_sso) as mock_cria_usuario_core_sso:
            with patch(api_atribuir_perfil_core_sso) as mock_atribuir_perfil_core_sso:
                response = jwt_authenticated_client_u.put(
                    f"/api/usuarios/{usuario_2.id}/", data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert usuario_2.unidades.filter(codigo_eol='271170').first(), "Deveria ter sido vinculado à unidade 271170."
    assert usuario_2.visoes.filter(nome='UE').first(), "Deveria ter sido vinculado à UE."
    assert usuario_2.visoes.filter(nome='DRE').first(), "Deveria continuar vinculado à DRE."
    assert usuario_2.visoes.filter(nome='SME').first(), "Deveria continuar vinculado à SME."

    mock_usuario_core_sso_or_none.assert_called_once_with(login='7211981')
    mock_atribuir_perfil_core_sso.assert_called_once_with(login='7211981', visao='UE')
    mock_cria_usuario_core_sso.assert_called_once_with(
        e_servidor=True,
        email='novoEmail@gmail.com',
        login='7211981',
        nome='Usuario 2'
    )


def test_atualizar_usuario_servidor_com_visoes(
        jwt_authenticated_client_u,
        usuario_3,
        usuario_2,
        visao_ue,
        visao_dre,
        visao_sme,
        grupo_1,
        grupo_2,
        unidade_ue_271170,
        unidade_diferente,
        dre
):

    assert not usuario_2.visoes.filter(nome='UE').first(), "Não deveria estar vinculado à UE antes do teste."
    assert not usuario_2.unidades.filter(codigo_eol='271170').first(), "Não deveria estar vinculado à unidade 271170 antes do teste."

    payload = {
        'e_servidor': True,
        'username': usuario_2.username,
        'name': usuario_2.name,
        'email': 'novoEmail@gmail.com',
        'visoes': [visao_ue.id, visao_dre.id],
        'unidade': "271170",
        'groups': [grupo_1.id],
        'id': usuario_2.id
    }

    api_usuario_core_sso_or_none = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.usuario_core_sso_or_none'
    api_cria_usuario_core_sso = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.cria_usuario_core_sso'
    api_atribuir_perfil_core_sso = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.atribuir_perfil_coresso'
    with patch(api_usuario_core_sso_or_none) as mock_usuario_core_sso_or_none:
        mock_usuario_core_sso_or_none.return_value = None
        with patch(api_cria_usuario_core_sso) as mock_cria_usuario_core_sso:
            with patch(api_atribuir_perfil_core_sso) as mock_atribuir_perfil_core_sso:
                response = jwt_authenticated_client_u.put(
                    f"/api/usuarios/{usuario_2.id}/", data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert usuario_2.visoes.filter(nome='UE').first(), "Deveria ter sido vinculado à visão UE."
    assert usuario_2.visoes.filter(nome='DRE').first(), "Deveria ter sido vinculado à visão DRE."
    assert usuario_2.unidades.filter(codigo_eol='271170').first(), "Deveria ter sido vinculado à unidade 271170."

    mock_usuario_core_sso_or_none.assert_called_once_with(login='7211981')
    mock_cria_usuario_core_sso.assert_called_once_with(
        e_servidor=True,
        email='novoEmail@gmail.com',
        login='7211981',
        nome='Usuario 2'
    )
    mock_atribuir_perfil_core_sso.assert_has_calls(
        [call(login='7211981', visao='UE'), call(login='7211981', visao='DRE')])


def test_atualizar_usuario_servidor_visao_sme(
        jwt_authenticated_client_u,
        usuario_3,
        usuario_2,
        visao_ue,
        visao_dre,
        visao_sme,
        grupo_1,
        grupo_2,
        unidade_ue_271170,
        unidade_diferente,
        dre
):

    assert not usuario_3.visoes.filter(nome='SME').first(), "Não deveria estar vinculado à SME antes do teste."

    payload = {
        'e_servidor': True,
        'username': usuario_3.username,
        'name': usuario_3.name,
        'email': 'novoEmail@gmail.com',
        'visao': "SME",
        'unidade': None,
        'groups': [
            grupo_1.id
        ]
    }

    api_usuario_core_sso_or_none = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.usuario_core_sso_or_none'
    api_cria_usuario_core_sso = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.cria_usuario_core_sso'
    api_atribuir_perfil_core_sso = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.atribuir_perfil_coresso'
    with patch(api_usuario_core_sso_or_none) as mock_usuario_core_sso_or_none:
        mock_usuario_core_sso_or_none.return_value = None
        with patch(api_cria_usuario_core_sso) as mock_cria_usuario_core_sso:
            with patch(api_atribuir_perfil_core_sso) as mock_atribuir_perfil_core_sso:
                response = jwt_authenticated_client_u.put(
                    f"/api/usuarios/{usuario_3.id}/", data=json.dumps(payload), content_type='application/json')

    result = response.json()

    esperado = {
        'username': usuario_3.username,
        'email': 'novoEmail@gmail.com',
        'name': 'Arthur Marques',
        'e_servidor': True,
        'groups': [grupo_1.id],
        'visoes': [visao_ue.id, visao_dre.id, visao_sme.id],
        'id': usuario_3.id
    }
    
    assert result['username'] == esperado['username']
    assert result['email'] == esperado['email']
    assert result['name'] == esperado['name']
    assert result['e_servidor'] == esperado['e_servidor']
    assert result['groups'] == esperado['groups']
    assert sorted(result['visoes']) == sorted(esperado['visoes'])
    assert result['id'] == esperado['id']

    assert usuario_3.visoes.filter(nome='SME').first(), "Deveria ter sido vinculado à visão SME."

    mock_usuario_core_sso_or_none.assert_called_once_with(login='7218198')
    mock_cria_usuario_core_sso.assert_called_once_with(
        e_servidor=True,
        email='novoEmail@gmail.com',
        login='7218198',
        nome='Arthur Marques'
    )

    mock_atribuir_perfil_core_sso.assert_called_once_with(login=usuario_3.username, visao='SME')


def test_atualizar_usuario_servidor_com_visoes_sem_definir_unidade(
        jwt_authenticated_client_u,
        usuario_3,
        usuario_2,
        visao_ue,
        visao_dre,
        visao_sme,
        grupo_1,
        grupo_2,
        unidade_ue_271170,
        unidade_diferente,
        dre
):

    assert usuario_2.unidades.filter(uuid=unidade_diferente.uuid).first(), "Deveria estar vinculado a essa UE."

    payload = {
        'e_servidor': True,
        'username': usuario_2.username,
        'name': usuario_2.name,
        'email': 'novoEmail@gmail.com',
        'visoes': [visao_ue.id, visao_dre.id],
        'unidade': None,
        'groups': [grupo_1.id]
    }

    api_usuario_core_sso_or_none = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.usuario_core_sso_or_none'
    api_cria_usuario_core_sso = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.cria_usuario_core_sso'
    api_atribuir_perfil_core_sso = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.atribuir_perfil_coresso'
    with patch(api_usuario_core_sso_or_none) as mock_usuario_core_sso_or_none:
        mock_usuario_core_sso_or_none.return_value = None
        with patch(api_cria_usuario_core_sso) as mock_cria_usuario_core_sso:
            with patch(api_atribuir_perfil_core_sso) as mock_atribuir_perfil_core_sso:
                response = jwt_authenticated_client_u.put(
                    f"/api/usuarios/{usuario_2.id}/", data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert usuario_2.unidades.filter(uuid=unidade_diferente.uuid).first(), "Deveria ter continuado vinculado à essa UE."
    assert usuario_2.visoes.filter(nome='UE').first(), "Deveria ter sido vinculado à visão UE."
    assert usuario_2.visoes.filter(nome='DRE').first(), "Deveria continuar vinculado à visão DRE."

    mock_usuario_core_sso_or_none.assert_called_once_with(login='7211981')
    mock_cria_usuario_core_sso.assert_called_once_with(
        e_servidor=True,
        email='novoEmail@gmail.com',
        login='7211981',
        nome='Usuario 2'
    )
    mock_atribuir_perfil_core_sso.assert_has_calls(
        [call(login='7211981', visao='UE'), call(login='7211981', visao='DRE')])
