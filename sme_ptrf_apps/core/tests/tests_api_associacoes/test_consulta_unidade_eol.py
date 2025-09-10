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


def test_consulta_unidade_retorna_nome_dre(jwt_authenticated_client_a):
    from unittest.mock import patch
    with patch('sme_ptrf_apps.core.api.views.associacoes_viewset.consulta_unidade') as mock_patch:
        resultado_esperado = {
            'codigo_eol': "786543",
            'nome': 'Unidade Nova',
            'nome_dre': 'DRE Butantã',
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
        assert 'nome_dre' in result
        assert result['nome_dre'] == resultado_esperado['nome_dre']


def test_consulta_unidade_codigo_eol_invalido(jwt_authenticated_client_a):
    from unittest.mock import patch
    with patch('sme_ptrf_apps.core.api.views.associacoes_viewset.consulta_unidade') as mock_patch:
        resultado_erro = {
            'erro': 'codigo_eol_inválido',
            'mensagem': 'Código eol 123 inválido. O código eol deve conter 6 dígitos.'
        }

        mock_patch.return_value = resultado_erro

        response = jwt_authenticated_client_a.get(
            f'/api/associacoes/eol/?codigo_eol=123', content_type='application/json')
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert result == resultado_erro


def test_consulta_unidade_codigo_eol_ja_cadastrado(jwt_authenticated_client_a):
    from unittest.mock import patch
    with patch('sme_ptrf_apps.core.api.views.associacoes_viewset.consulta_unidade') as mock_patch:
        resultado_erro = {
            'erro': 'codigo_eol_ja_cadastrado',
            'mensagem': 'O código eol 200204 já está vinculado a uma associação.'
        }

        mock_patch.return_value = resultado_erro

        response = jwt_authenticated_client_a.get(
            f'/api/associacoes/eol/?codigo_eol=200204', content_type='application/json')
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert result == resultado_erro


def test_consulta_unidade_erro_generico_mapeia_para_400(jwt_authenticated_client_a):
    from unittest.mock import patch
    with patch('sme_ptrf_apps.core.api.views.associacoes_viewset.consulta_unidade') as mock_patch:
        resultado_erro = {
            'erro': 'erro',
            'mensagem': 'Erro ao consultar código eol: timeout'
        }

        mock_patch.return_value = resultado_erro

        response = jwt_authenticated_client_a.get(
            f'/api/associacoes/eol/?codigo_eol=999999', content_type='application/json')
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert result == resultado_erro


def test_consulta_unidade_passa_codigo_eol_para_service(jwt_authenticated_client_a):
    from unittest.mock import patch
    with patch('sme_ptrf_apps.core.api.views.associacoes_viewset.consulta_unidade') as mock_patch:
        mock_patch.return_value = {
            'codigo_eol': "123456",
            'nome': 'Unidade X',
            'nome_dre': 'DRE Y',
            'email': '',
            'telefone': '',
            'numero': '',
            'tipo_logradouro': '',
            'logradouro': '',
            'bairro': '',
            'cep': ''
        }

        response = jwt_authenticated_client_a.get(
            f'/api/associacoes/eol/?codigo_eol=123456', content_type='application/json')

        assert response.status_code == status.HTTP_200_OK
        # Verifica que a view repassou corretamente o parâmetro para o service
        mock_patch.assert_called_once_with('123456')
