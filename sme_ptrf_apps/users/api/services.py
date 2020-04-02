import logging

import environ
import requests

env = environ.Env()
AUTENTICA_CORESSO_API_TOKEN = env('AUTENTICA_CORESSO_API_TOKEN', default='')
AUTENTICA_CORESSO_API_URL = env('AUTENTICA_CORESSO_API_URL', default='')

LOG = logging.getLogger(__name__)


class AutenticacaoService:
    DEFAULT_HEADERS = {
        'Content-Type': 'application/json',
        'Authorization': f'Token {AUTENTICA_CORESSO_API_TOKEN}'}
    DEFAULT_TIMEOUT = 10

    @classmethod
    def autentica(cls, login, senha):
        payload = {'login': login, 'senha': senha}
        try:
            LOG.info("Autenticando no sme-autentica. Login: %s", login)
            response = requests.post(
                f"{AUTENTICA_CORESSO_API_URL}/autenticacao/",
                headers=cls.DEFAULT_HEADERS,
                timeout=cls.DEFAULT_TIMEOUT,
                json=payload         
            )
            return response
        except Exception as e:
            LOG.info("ERROR - %s", str(e))
            raise e
