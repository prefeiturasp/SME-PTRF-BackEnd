import json
from unittest.mock import patch

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

def test_consulta_informacao_usuario_sem_username(jwt_authenticated_client_u):
    response = jwt_authenticated_client_u.get(f'/api/usuarios/status/?username=')
    result = json.loads(response.content)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == "Parâmetro username obrigatório."


def test_get_usuario_status_cadastrado_core_sso_nao_cadastrado_sig_escola(jwt_authenticated_client_u):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.usuario_core_sso_or_none'
    with patch(path) as mock_get:
        data = {
            'cpf': '12808888813',
            'nome': 'LUCIMARA CARDOSO RODRIGUES',
            'codigoRf': '12345',
            'email': 'tutu@gmail.com',
            'emailValido': True
        }

        mock_get.return_value = data

        username = '12345'
        response = jwt_authenticated_client_u.get(f'/api/usuarios/status/?username={username}')

        esperado = {
            'usuario_core_sso': {
                'info_core_sso': data,
                'mensagem': 'Usuário encontrado no CoreSSO.'
            },
            'usuario_sig_escola': {
                'info_sig_escola': None,
                'mensagem': 'Usuário não encontrado no Sig.Escola.'
            },
            'validacao_username': {'mensagem': '', 'username_e_valido': True}
        }

        result = json.loads(response.content)
        assert response.status_code == status.HTTP_200_OK
        assert result == esperado


def test_get_usuario_status_servidor_cadastrado_sig_escola_nao_cadastrado_core_sso(jwt_authenticated_client_u):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.usuario_core_sso_or_none'
    with patch(path) as mock_get:

        mock_get.return_value = None

        username = '7210418'
        response = jwt_authenticated_client_u.get(f'/api/usuarios/status/?username={username}&servidor=True')

        usuario_sig_escola_esperado = {
            'info_sig_escola': {
                'visoes': ['UE'],
                'unidades': ['123456',],
            },
            'mensagem': 'Usuário encontrado no Sig.Escola.'
        }
        esperado = {
            'usuario_core_sso': {
                'info_core_sso': None,
                'mensagem': 'Usuário não encontrado no CoreSSO.'
            },
            'usuario_sig_escola': usuario_sig_escola_esperado,
            'validacao_username': {
                'username_e_valido': True,
                'mensagem': "",
            }
        }

        result = json.loads(response.content)
        assert response.status_code == status.HTTP_200_OK
        assert result == esperado


def test_get_usuario_status_nao_servidor_username_invalido(jwt_authenticated_client_u):
    """ O username de um não servidor que não é um CPF válido deve retornar informação de username inválido.
    """
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.usuario_core_sso_or_none'
    with patch(path) as mock_get:

        mock_get.return_value = None

        username = '745745'
        response = jwt_authenticated_client_u.get(f'/api/usuarios/status/?username={username}&servidor=False')

        usuario_sig_escola_esperado = {
            'info_sig_escola': None,
            'mensagem': 'Usuário não encontrado no Sig.Escola.'
        }
        esperado = {
            'usuario_core_sso': {
                'info_core_sso': None,
                'mensagem': 'Usuário não encontrado no CoreSSO.'
            },
            'usuario_sig_escola': usuario_sig_escola_esperado,
            'validacao_username': {
                'username_e_valido': False,
                'mensagem': "O id de um usuário não servidor deve ser um CPF válido (apenas dígitos).",
            }
        }

        result = json.loads(response.content)
        assert response.status_code == status.HTTP_200_OK
        assert result == esperado

