import json
import pytest

from unittest.mock import patch, call

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

    assert not usuario_2.visoes.filter(nome='UE').first(), "Não deveria estar vinculado à UE antes do teste."
    assert not usuario_2.unidades.filter(codigo_eol='271170').first(), "Não deveria estar vinculado à unidade 271170 antes do teste."

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

    result = response.json()

    esperado = {
        'username': usuario_2.username,
        'email': 'novoEmail@gmail.com',
        'name': usuario_2.name,
        'e_servidor': True,
        'groups': [grupo_1.id],
        'visoes': [visao_ue.id, visao_dre.id, visao_sme.id],
    }

    assert usuario_2.visoes.filter(nome='UE').first(), "Deveria ter sido vinculado à visão UE."
    assert usuario_2.unidades.filter(codigo_eol='271170').first(), "Deveria ter sido vinculado à unidade 271170."
    assert result == esperado

    mock_usuario_core_sso_or_none.assert_called_once_with(login='7211981')
    mock_cria_usuario_core_sso.assert_called_once_with(
        e_servidor=True,
        email='novoEmail@gmail.com',
        login='7211981',
        nome='Usuario 2'
    )
    mock_atribuir_perfil_core_sso.assert_called_once_with(login='7211981', visao='UE')


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

    result = response.json()

    esperado = {
        'username': usuario_2.username,
        'email': 'novoEmail@gmail.com',
        'name': usuario_2.name,
        'e_servidor': True,
        'groups': [grupo_1.id],
        'visoes': [visao_ue.id, visao_dre.id],
    }

    assert usuario_2.visoes.filter(nome='UE').first(), "Deveria ter sido vinculado à visão UE."
    assert usuario_2.unidades.filter(codigo_eol='271170').first(), "Deveria ter sido vinculado à unidade 271170."
    assert result == esperado

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
    }

    assert usuario_3.visoes.filter(nome='SME').first(), "Deveria ter sido vinculado à visão SME."
    assert result == esperado

    mock_usuario_core_sso_or_none.assert_called_once_with(login='7218198')
    mock_cria_usuario_core_sso.assert_called_once_with(
        e_servidor=True,
        email='novoEmail@gmail.com',
        login='7218198',
        nome='Arthur Marques'
    )

    mock_atribuir_perfil_core_sso.assert_called_once_with(login=usuario_3.username, visao='SME')
