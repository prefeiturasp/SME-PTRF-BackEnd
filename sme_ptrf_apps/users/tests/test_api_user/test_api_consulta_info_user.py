import json
from unittest.mock import patch

import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_consulta_informacao_usuario(jwt_authenticated_client_u):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.informacao_usuario_sgp'
    with patch(path) as mock_get:
        data = {
            'cpf': '12808888813',
            'nome': 'LUCIMARA CARDOSO RODRIGUES',
            'codigoRf': '7210418',
            'email': 'tutu@gmail.com',
            'emailValido': True
        }

        mock_get.return_value = data

        response = jwt_authenticated_client_u.get(f'/api/usuarios/consultar/?username={7210418}')
        result = json.loads(response.content)
        assert response.status_code == status.HTTP_200_OK
        assert result == data


def test_consulta_informacao_usuario_sem_username(jwt_authenticated_client_u):
    response = jwt_authenticated_client_u.get(f'/api/usuarios/consultar/?username=')
    result = json.loads(response.content)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == "Parâmetro username obrigatório."


