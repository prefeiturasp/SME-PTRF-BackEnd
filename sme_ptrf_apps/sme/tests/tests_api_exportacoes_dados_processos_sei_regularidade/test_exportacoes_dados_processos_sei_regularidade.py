import json
import pytest

from unittest.mock import Mock

from rest_framework.status import HTTP_201_CREATED

from sme_ptrf_apps.sme.tasks import exportar_processos_sei_regularidade_async

pytestmark = pytest.mark.django_db


def test_exportacoes_dados_processos_sei_regularidade(jwt_authenticated_client_sme, usuario_permissao_sme, monkeypatch):
    url = f'/api/exportacoes-dados/processos-sei-regularidade/'
    resultado_esperado = {
        'response': 'O arquivo está sendo gerado e será enviado para a central de download após conclusão.'
    }

    mock_exportar_processos_sei_regularidade_async = Mock()
    monkeypatch.setattr(exportar_processos_sei_regularidade_async, 'delay',
                        mock_exportar_processos_sei_regularidade_async)

    response = jwt_authenticated_client_sme.get(
        url,
        content_type='multipart/form-data')

    result = json.loads(response.content)

    # Testa o resultado da requisição
    assert response.status_code == HTTP_201_CREATED
    assert result == resultado_esperado

    # Testa se a função mockada foi chamada com os parâmetros corretos
    mock_exportar_processos_sei_regularidade_async.assert_called_once_with(
        username=usuario_permissao_sme.username
    )
