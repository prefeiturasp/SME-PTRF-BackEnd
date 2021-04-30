from brazilnum.cpf import validate_cpf
from requests import ReadTimeout, ConnectTimeout

from sme_ptrf_apps.users.services import SmeIntegracaoService, SmeIntegracaoException
from sme_ptrf_apps.users.services.carga_usuario_service import CargaUsuarioException, logger


def cria_ou_atualiza_usuario_core_sso(dados_usuario):
    """ Verifica se usuário já existe no CoreSSO e cria se não existir

    :param dados_usuario: {
            "login": "123456",
            "visao": "UE",
            "eol_unidade": "1234",
            "email": "teste@teste.com",
            "nome": "Jose Testando",
            "servidor_s_n": "S",
        }
    """
    from requests import ConnectTimeout, ReadTimeout

    try:
        info_user_core = SmeIntegracaoService.usuario_core_sso_or_none(login=dados_usuario['login'])

        if not info_user_core:
            # Valida o nome
            if not dados_usuario['nome']:
                raise CargaUsuarioException(f"Nome é necessário para criação do usuário ({dados_usuario['login']}).")

            # Valida login no caso de não servidor
            if dados_usuario['servidor_s_n'] == "N" and not validate_cpf(dados_usuario['login']):
                raise CargaUsuarioException(f"Login de não servidor ({dados_usuario['login']}) não é um CPF válido.")

            SmeIntegracaoService.cria_usuario_core_sso(
                login=dados_usuario['login'],
                nome=dados_usuario['nome'],
                email=dados_usuario["email"] if dados_usuario["email"] else "",
                e_servidor=dados_usuario['servidor_s_n'] == "S"
            )
            logger.info(f"Criado usuário no CoreSSO {dados_usuario['login']}.")

        if info_user_core and dados_usuario["email"] and info_user_core["email"] != dados_usuario["email"]:
            SmeIntegracaoService.redefine_email(dados_usuario['login'], dados_usuario["email"])
            logger.info(f"Atualizado e-mail do usuário no CoreSSO {dados_usuario['login']}, {dados_usuario['email']}.")

        if dados_usuario["visao"] :
            SmeIntegracaoService.atribuir_perfil_coresso(login=dados_usuario['login'], visao=dados_usuario['visao'])
            logger.info(f"Visão {dados_usuario['visao']} vinculada ao usuário {dados_usuario['login']} no CoreSSO.")

    except SmeIntegracaoException as e:
        raise CargaUsuarioException(f'Erro {str(e)} ao criar/atualizar usuário {dados_usuario["login"]} no CoreSSO.')

    except ReadTimeout:
        raise CargaUsuarioException(f'Erro de ReadTimeout ao tentar criar/atualizar usuário {dados_usuario["login"]} no CoreSSO.')

    except ConnectTimeout:
        raise CargaUsuarioException(f'Erro de ConnectTimeout ao tentar criar/atualizar usuário {dados_usuario["login"]} no CoreSSO.')
