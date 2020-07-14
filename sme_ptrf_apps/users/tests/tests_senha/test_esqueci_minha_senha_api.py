import json
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.django_db


def test_esqueci_minha_senha(jwt_authenticated_client, usuario):
    path = 'sme_ptrf_apps.users.api.views.senha_viewset.EsqueciMinhaSenhaSerializer.update'
    with patch(path) as mock_get:
        usuario.hash_redefinicao = usuario.create_hash
        mock_get.return_value = usuario

        data = {
            'username': usuario.username
        }

        response = jwt_authenticated_client.put(
            f'/api/esqueci-minha-senha/{usuario.username}/', data=json.dumps(data), content_type='application/json')
        result = json.loads(response.content)
        esperado = {'username': '7210418', 'email': 'sme@amcom.com.br'}

        assert result == esperado
