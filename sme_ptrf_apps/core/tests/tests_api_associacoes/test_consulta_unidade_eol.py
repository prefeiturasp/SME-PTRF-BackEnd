import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_consulta_unidade(jwt_authenticated_client_a):
    from unittest.mock import patch
    with patch('sme_ptrf_apps.core.api.views.associacoes_viewset.consulta_unidade') as mock_patch:
        resultado_esperado = {
            'codigo_eol': "786543",
            'nome': 'Unidade Nova',
            'email': 'unidadenova@gmail.com',
            'telefone': '11992735056',
            'numero': '89',
            'tipo_logradouro': 'Rua',
            'logradouro': 'Flamengo',
            'bairro': 'Ferreira',
            'cep': '05524160'
        }

        mock_patch.return_value = resultado_esperado

        response = jwt_authenticated_client_a.get(
            f'/api/associacoes/eol/?codigo_eol=786543', content_type='application/json')
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_200_OK
        assert result == resultado_esperado
