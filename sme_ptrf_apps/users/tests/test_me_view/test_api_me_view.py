import pytest

from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

ME_URL = '/api/me'


def test_me_view_sem_autenticacao_retorna_401():
    api_client = APIClient()

    response = api_client.get(ME_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_me_view_autenticado_retorna_dict_vazio(me_client):
    """MeView está desativada temporariamente (ver docstring da view): não recalcula
    mais nada, só confirma que o usuário está autenticado e devolve {}.

    Isso evita reintroduzir o incidente de perda de acesso a unidades causado por
    valida_unidades_do_usuario() (chamado indiretamente via GestaoUsuarioService/
    LoginUsuarioService) rodando a cada reload de página em vez de só no login.
    """
    response = me_client.get(ME_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {}
