import logging
import json
import requests

from django.conf import settings
from rest_framework import status

logger = logging.getLogger(__name__)


class SmeIntegracaoException(Exception):
    pass


class SmeIntegracaoService:
    headers = {
        'accept': 'application/json',
        'x-api-eol-key': f'{settings.SME_INTEGRACAO_TOKEN}'
    }
    timeout = 20

    @classmethod
    def redefine_senha(cls, registro_funcional, senha):
        """Se a nova senha for uma das senhas padões, a API do SME INTEGRAÇÃO
        não deixa fazer a atualização.
        Para resetar para a senha padrão é preciso usar o endpoint ReiniciarSenha da API SME INTEGRAÇÃO"""
        logger.info('Alterando senha.')
        try:
            data = {
                'Usuario': registro_funcional,
                'Senha': senha
            }
            response = requests.post(f'{settings.SME_INTEGRACAO_URL}/api/AutenticacaoSgp/AlterarSenha', data=data, headers=cls.headers)
            if response.status_code == status.HTTP_200_OK:
                result = "OK"
                return result
            else:
                logger.info("Erro ao redefinir senha: %s", response.content.decode('utf-8'))
                raise SmeIntegracaoException(f"Erro ao redefinir senha: {response.content.decode('utf-8')}")
        except Exception as err:
            raise SmeIntegracaoException(str(err))

    @classmethod
    def redefine_email(cls, registro_funcional, email):
        logger.info('Alterando email.')
        try:
            data = {
                'Usuario': registro_funcional,
                'Email': email
            }
            response = requests.post(f'{settings.SME_INTEGRACAO_URL}/api/AutenticacaoSgp/AlterarEmail', data=data, headers=cls.headers)
            if response.status_code == status.HTTP_200_OK:
                result = "OK"
                return result
            else:
                logger.info("Erro ao redefinir email: %s", response.json())
                raise SmeIntegracaoException('Erro ao redefinir email')
        except Exception as err:
            raise SmeIntegracaoException(str(err))


    @classmethod
    def informacao_usuario_sgp(cls, login):
        logger.info('Consultando informação de %s.', login)
        try:
            response = requests.get(f'{settings.SME_INTEGRACAO_URL}/api/AutenticacaoSgp/{login}/dados', headers=cls.headers)
            if response.status_code == status.HTTP_200_OK:
                return response.json()
            else:
                logger.info("Dados não encontrados: %s", response)
                raise SmeIntegracaoException('Dados não encontrados.')
        except Exception as err:
            logger.info("Erro ao consultar informação: %s", str(err))
            raise SmeIntegracaoException(str(err))

    @classmethod
    def usuario_core_sso_or_none(cls, login):
        logger.info('Consultando informação de %s.', login)
        try:
            response = requests.get(f'{settings.SME_INTEGRACAO_URL}/api/AutenticacaoSgp/{login}/dados', headers=cls.headers)
            if response.status_code == status.HTTP_200_OK:
                return response.json()
            else:
                logger.info(f"Usuário {login} não encontrado no CoreSSO: {response}")
                return None
        except Exception as err:
            logger.info(f"Erro ao procurar usuário {login} no CoreSSO: {str(err)}")
            raise SmeIntegracaoException(str(err))


    @classmethod
    def atribuir_perfil_coresso(cls, login, visao):
        """ Atribuição de Perfil:

        /api/perfis/servidores/{codigoRF}/perfil/{perfil}/atribuirPerfil - GET
        CodigoRf - RF ou CPF do usuário
        Perfil - Guid do perfil a ser atribuído

        :param login:
        :param visao:
        :return:
        """
        logger.info(f'Atribuindo visão {visao} ao usuário {login}.')
        sys_grupo_ids = {
            "UE": settings.SYS_GRUPO_ID_UE,
            "DRE": settings.SYS_GRUPO_ID_DRE,
            "SME": settings.SYS_GRUPO_ID_SME,
            "PTRF": settings.SYS_GRUPO_ID_PTRF
        }
        try:
            grupo_id = sys_grupo_ids[visao]
            url = f'{settings.SME_INTEGRACAO_URL}/api/perfis/servidores/{login}/perfil/{grupo_id}/atribuirPerfil'
            response = requests.get(url, headers=cls.headers)
            if response.status_code == status.HTTP_200_OK:
                return ""
            else:
                logger.info("Falha ao tentar fazer atribuição de perfil: %s", response)
                raise SmeIntegracaoException('Falha ao fazer atribuição de perfil.')
        except Exception as err:
            logger.info("Erro ao tentar fazer atribuição de perfil: %s", str(err))
            raise SmeIntegracaoException(str(err))

    @classmethod
    def get_dados_unidade_eol(cls, codigo_eol):
        """ Consulta dados de uma unidade no EOL

            /api/escolas/dados/{codigo_eol}

        :param codigo_eol: Código EOL da unidade
        :return: Dados cadastrais da Unidade
        """
        logger.info(f'Consultando no eol dados da unidade {codigo_eol}.')
        try:
            url = f'{settings.SME_INTEGRACAO_URL}/api/escolas/dados/{codigo_eol}'
            response = requests.get(url, headers=cls.headers)
            if response.status_code == status.HTTP_200_OK:
                return response
            else:
                logger.info("Falha ao tentar consultar dados da unidade no eol: %s", response)
                raise SmeIntegracaoException('Falha ao tentar consultar dados da unidade no eol.')
        except Exception as err:
            logger.info("Erro ao tentar ao consulta dados da unidade do eol: %s", str(err))
            raise SmeIntegracaoException(str(err))

    @classmethod
    def login_nao_servidor_valido(cls, login):
        return True

    @classmethod
    def cria_usuario_core_sso(cls, login, nome, email, e_servidor=False):
        """ Cria um novo usuário no CoreSSO

        :param login:       login do usuário
        :param nome:        nome completo do usuário
        :param email:       e-mail do usuário
        :param e_servidor:  True se for servidor. False se não for servidor.
        :return:

        /api/v1/usuarios/coresso - POST
            {
              "nome": "Nome do Usuário",
              "documento": "CPF em caso de não funcionário, caso de funcionário, enviar vazio",
              "codigoRf": "Código RF do funcionário, caso não funcionario, enviar vazio",
              "email": "Email do usuário"
            }
        """

        headers = {
            'accept': 'application/json',
            'x-api-eol-key': f'{settings.SME_INTEGRACAO_TOKEN}',
            'Content-Type': 'application/json-patch+json'
        }

        logger.info('Criando usuário no CoreSSO.')

        if not e_servidor and not cls.login_nao_servidor_valido(login):
            raise SmeIntegracaoException('Login inválido para um não servidor. Necessário ser um CPF válido sem pontos.')

        try:
            url = f'{settings.SME_INTEGRACAO_URL}/api/v1/usuarios/coresso'

            payload = json.dumps({
                "nome": nome,
                "documento": login if not e_servidor else "",
                "codigoRf": login if e_servidor else "",
                "email": email
            })

            response = requests.request("POST", url, headers=headers, data=payload)

            if response.status_code == status.HTTP_200_OK:
                result = "OK"
                return result
            else:
                logger.info("Erro ao redefinir email: %s", response.json())
                raise SmeIntegracaoException(f'Erro ao tentar criar o usuário {nome}.')
        except Exception as err:
            raise SmeIntegracaoException(str(err))
