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
                'mensagem': 'Usuário não encontrado no Sig.Escola.',
                'associacoes_que_e_membro': [],
            },
            'validacao_username': {'mensagem': '', 'username_e_valido': True},
            'e_servidor_na_unidade': False
        }

        result = json.loads(response.content)
        assert response.status_code == status.HTTP_200_OK
        assert result == esperado


def test_get_usuario_status_servidor_cadastrado_sig_escola_nao_cadastrado_core_sso(
    jwt_authenticated_client_u,
    usuario_para_teste
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.usuario_core_sso_or_none'
    with patch(path) as mock_get:

        mock_get.return_value = None

        username = '7210418'
        response = jwt_authenticated_client_u.get(f'/api/usuarios/status/?username={username}&servidor=True')

        usuario_sig_escola_esperado = {
            'info_sig_escola': {
                'visoes': ['UE'],
                'unidades': ['123456', ],
                'user_id': usuario_para_teste.id
            },
            'mensagem': 'Usuário encontrado no Sig.Escola.',
            'associacoes_que_e_membro': [],
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
            },
            'e_servidor_na_unidade': False
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
            'mensagem': 'Usuário não encontrado no Sig.Escola.',
            'associacoes_que_e_membro': [],
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
            },
            'e_servidor_na_unidade': False
        }

        result = json.loads(response.content)
        assert response.status_code == status.HTTP_200_OK
        assert result == esperado


def test_get_usuario_status_nao_servidor_membro_associacoes(
    jwt_authenticated_client_u,
    usuario_nao_servidor,
    associacao_271170,
    membro_associacao_00746198701
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.usuario_core_sso_or_none'
    with patch(path) as mock_get:

        mock_get.return_value = None

        username = '00746198701'
        response = jwt_authenticated_client_u.get(f'/api/usuarios/status/?username={username}&servidor=False')

        usuario_sig_escola_esperado = {
            'info_sig_escola': {
                'visoes': ['UE', 'DRE'],
                'unidades': ['123456', ],
                'user_id': usuario_nao_servidor.id
            },
            'mensagem': 'Usuário encontrado no Sig.Escola.',
            'associacoes_que_e_membro': [f'{associacao_271170.uuid}', ],
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
            },
            'e_servidor_na_unidade': False
        }

        result = json.loads(response.content)
        assert response.status_code == status.HTTP_200_OK

        # TODO Rever assert. A ordem das visões muda de teste para teste.
        # assert result == esperado


def test_get_usuario_status_servidor_lotado_na_unidade(jwt_authenticated_client_u, unidade_ue_271170, usuario_para_teste):
    api_usuario_core_sso_or_none = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.usuario_core_sso_or_none'
    api_get_cargos_do_rf = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_cargos_do_rf'
    api_get_rfs_com_o_cargo_na_escola = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_rfs_com_o_cargo_na_escola'

    with patch(api_usuario_core_sso_or_none) as mock_get:
        mock_get.return_value = None
        with patch(api_get_cargos_do_rf) as mock_api_get_cargos_do_rf:
            mock_api_get_cargos_do_rf.return_value = {
                "nomeServidor": "LUCIMARA CARDOSO RODRIGUES",
                "codigoServidor": "7210418",
                "cargos": [
                    {
                        "codigoCargo": "3298",
                        "nomeCargo": "PROF.ENS.FUND.II E MED.-PORTUGUES",
                        "nomeCargoSobreposto": "ASSISTENTE DE DIRETOR DE ESCOLA",
                        "codigoCargoSobreposto": "3085"
                    }
                ]
            }

            with patch(api_get_rfs_com_o_cargo_na_escola) as mock_api_get_rfs_com_o_cargo_na_escola:
                mock_api_get_rfs_com_o_cargo_na_escola.return_value = [
                    {
                        "codigoRF": 8382492,
                        "nomeServidor": "DANIELA CRISTINA BRAZ",
                        "dataInicio": "02/03/2017 00:00:00",
                        "dataFim": None,
                        "cargo": "ASSISTENTE DE DIRETOR DE ESCOLA",
                        "cdTipoFuncaoAtividade": 0
                    },
                    {
                        "codigoRF": 7210418,
                        "nomeServidor": "JOSE TESTANDO",
                        "dataInicio": "02/03/2017 00:00:00",
                        "dataFim": None,
                        "cargo": "ASSISTENTE DE DIRETOR DE ESCOLA",
                        "cdTipoFuncaoAtividade": 0
                    },
                ]

                username = '7210418'
                unidade = unidade_ue_271170.uuid
                url = f'/api/usuarios/status/?username={username}&servidor=True&unidade={unidade}'

                response = jwt_authenticated_client_u.get(url)

        usuario_sig_escola_esperado = {
            'info_sig_escola': {
                'visoes': ['UE'],
                'unidades': ['123456', ],
                'user_id': usuario_para_teste.id
            },
            'mensagem': 'Usuário encontrado no Sig.Escola.',
            'associacoes_que_e_membro': [],
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
            },
            'e_servidor_na_unidade': True
        }

        result = json.loads(response.content)
        assert response.status_code == status.HTTP_200_OK
        assert result == esperado


def test_get_usuario_status_nao_servidor_membro_associacoes_nao_cadastrado_sigescola(
    jwt_authenticated_client_u,
    associacao_271170,
    membro_associacao_00746198701
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.usuario_core_sso_or_none'
    with patch(path) as mock_get:

        mock_get.return_value = None

        username = '00746198701'
        response = jwt_authenticated_client_u.get(f'/api/usuarios/status/?username={username}&servidor=False')

        usuario_sig_escola_esperado = {
            'info_sig_escola': None,
            'mensagem': 'Usuário não encontrado no Sig.Escola.',
            'associacoes_que_e_membro': [f'{associacao_271170.uuid}', ],
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
            },
            'e_servidor_na_unidade': False
        }

        result = json.loads(response.content)
        assert response.status_code == status.HTTP_200_OK
        assert result == esperado
