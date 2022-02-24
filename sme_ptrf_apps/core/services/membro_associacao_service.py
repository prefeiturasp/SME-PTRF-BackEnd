import logging

import requests
from django.conf import settings
from rest_framework import status

logger = logging.getLogger(__name__)


class SmeIntegracaoApiException(Exception):
    pass


class SmeIntegracaoApiService:
    headers = {
        'accept': 'application/json',
        'x-api-eol-key': f'{settings.SME_INTEGRACAO_TOKEN}',
        'Content-Type': 'application/json-patch+json'
    }

    timeout = 20

    @classmethod
    def get_informacao_aluno(cls, codigo_eol):
        logger.info('Buscando informações na API EOL SmeIntegração para o código eol: %s.', codigo_eol)
        try:
            response = requests.get(f'{settings.SME_INTEGRACAO_URL}/api/alunos/alunos?codigosAluno={codigo_eol}',
                                    headers=cls.headers, timeout=cls.timeout)
        except Exception as e:
            logger.info(f'Erro ao acessar api smeintegracaoapi.sme.prefeitura.sp.gov.br: {str(e)}')
            raise SmeIntegracaoApiException('Erro ao consultar EOL. Tente mais tarde.')

        logger.info(response.url)
        logger.info(response)

        if response.status_code == status.HTTP_200_OK:
            results = response.json()
            if len(results) == 1:
                return results[0]
            else:
                msg = 'Código não encontrado.'
                logger.error(msg)
                raise SmeIntegracaoApiException(msg)
        else:
            raise SmeIntegracaoApiException('Código inválido.')


class TerceirizadasException(Exception):
    pass


class TerceirizadasService:
    headers = {
        'Authorization': f'Token {settings.EOL_API_TERCEIRIZADAS_TOKEN}'
    }

    timeout = 20

    @classmethod
    def get_informacao_servidor(cls, registro_funcional):
        logger.info("Buscando informações do servidor com RF: %s", registro_funcional)
        response = requests.get(f'{settings.EOL_API_TERCEIRIZADAS_URL}/cargos/{registro_funcional}',
                                headers=cls.headers, timeout=cls.timeout)
        if response.status_code == status.HTTP_200_OK:
            results = response.json()['results']
            logger.info("Dados do servidor: %r", results)
            if len(results) >= 1:
                return results
            raise TerceirizadasException(f'Não foram encontrados resultados para o RF: {registro_funcional}.')
        else:
            raise TerceirizadasException(f'API EOL com erro. Status: {response.status_code}')

