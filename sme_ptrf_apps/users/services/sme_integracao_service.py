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

        /api/v1/usuarios/coresso - POST

        Payload =
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

    @classmethod
    def get_cargos_do_rf(cls, rf):
        """ Retorna os cargos de dado RF.

        (get) /api/perfis/servidores/{codigoRF}/cargos

        {
          "nomeServidor": "LUCIMARA CARDOSO RODRIGUES",
          "codigoServidor": "7210418",
          "cargos": [
            {
              "codigoCargo": "3298",
              "nomeCargo": "PROF.ENS.FUND.II E MED.-PORTUGUES",
              "nomeCargoSobreposto": "ASSISTENTE DE DIRETOR DE ESCOLA",
              "codigoCargoSobreposto": "3085"
            },
          ]
        }

        """
        logger.info('Consultando informação de %s.', rf)
        try:
            response = requests.get(f'{settings.SME_INTEGRACAO_URL}/api/perfis/servidores/{rf}/cargos',
                                    headers=cls.headers)
            if response.status_code == status.HTTP_200_OK:
                return response.json()
            else:
                logger.info("Dados não encontrados: %s", response)
                raise SmeIntegracaoException('Dados não encontrados.')
        except Exception as err:
            logger.info("Erro ao consultar informação: %s", str(err))
            raise SmeIntegracaoException(str(err))

    @classmethod
    def get_rfs_com_o_cargo_na_escola(cls, codigo_cargo, codigo_eol):
        """ Retorna lista de RFs com dado cargo em dada escola

        (get) /api/escolas/{codigo_eol}/funcionarios/cargos/{codigo_cargo}

        [
          {
            "codigoRF": 8382492,
            "nomeServidor": "DANIELA CRISTINA BRAZ",
            "dataInicio": "02/03/2017 00:00:00",
            "dataFim": null,
            "cargo": "ASSISTENTE DE DIRETOR DE ESCOLA         ",
            "cdTipoFuncaoAtividade": 0
          }
        ]

        """
        logger.info(f'Consultando ocupantes do cargo {codigo_cargo} na UE {codigo_eol}.')
        url = f'{settings.SME_INTEGRACAO_URL}/api/escolas/{codigo_eol}/funcionarios/cargos/{codigo_cargo}'
        try:
            response = requests.get(url, headers=cls.headers)
            if response.status_code == status.HTTP_200_OK:
                return response.json()
            else:
                logger.info("Dados não encontrados: %s", response)
                raise SmeIntegracaoException('Dados não encontrados.')
        except Exception as err:
            logger.info(f'Consultando ocupantes do cargo {codigo_cargo} na UE {codigo_eol}: {str(err)}.')
            raise SmeIntegracaoException(str(err))

    @classmethod
    def get_cargos_do_rf_na_escola(cls, rf, codigo_eol):
        """ Retorna os cargos que dado RF tem em dada escola (código eol) ou [] se não tiver.
        """
        cargos_do_rf_na_escola = []

        try:
            result_cargos_do_rf = cls.get_cargos_do_rf(rf=rf)
        except Exception as err:
            logger.info(f'Erro ao consultar cargos do rf {rf}: {err}')
            result_cargos_do_rf = None

        cargos_do_rf = result_cargos_do_rf["cargos"] if result_cargos_do_rf else []

        if not cargos_do_rf:
            return []

        for cargo in cargos_do_rf:

            try:
                rfs_com_o_cargo_na_escola = cls.get_rfs_com_o_cargo_na_escola(
                    codigo_eol=codigo_eol,
                    codigo_cargo=cargo["codigoCargo"]
                )
                if rfs_com_o_cargo_na_escola:
                    cargos_do_rf_na_escola = list(filter(lambda d: d['codigoRF'] == int(rf), rfs_com_o_cargo_na_escola))

            except Exception as err:
                logger.info(f'Erro ao consultar rfs com o cargo {cargo["codigoCargo"]} na escola {codigo_eol}: {err}')
                continue

            if cargos_do_rf_na_escola:
                break

        return cargos_do_rf_na_escola
