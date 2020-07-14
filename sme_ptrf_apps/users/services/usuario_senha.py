import json
import logging

import requests
from django.conf import settings
from rest_framework import status

logger = logging.getLogger(__name__)


class SmeIntegracaoException(Exception):
    pass


class SmeIntegracaoService:
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
            response = requests.post(f'{settings.SME_INTEGRACAO_URL}/api/AutenticacaoSgp/AlterarSenha', data=data)
            logger.info(response.json())
            if response.status_code == status.HTTP_200_OK:
                result = response.json()
                return result
            else:
                logger.info("Erro ao redefinir senha: %s", response.json())
                raise SmeIntegracaoException('Erro ao redefinir senha')
        except Exception as err:
            raise SmeIntegracaoException(str(err))
