import json
import pytest

from unittest.mock import Mock

from rest_framework.status import HTTP_201_CREATED

from sme_ptrf_apps.sme.tasks import exportar_saldos_bancarios_async

pytestmark = pytest.mark.django_db


def test_exportacoes_dados_saldos_bancarios(jwt_authenticated_client_sme, usuario_permissao_sme, monkeypatch):
    url = '/api/exportacoes-dados/saldos-bancarios/'
    resultado_esperado = {
        'response': 'O arquivo está sendo gerado e será enviado para a central de download após conclusão.'
    }

    mock_exportar_saldos_bancarios_async = Mock()
    monkeypatch.setattr(exportar_saldos_bancarios_async, 'delay', mock_exportar_saldos_bancarios_async)

    response = jwt_authenticated_client_sme.get(
        url,
        content_type='multipart/form-data')

    result = json.loads(response.content)

    # Testa o resultado da requisição
    assert response.status_code == HTTP_201_CREATED
    assert result == resultado_esperado

    # Testa se a função mockada foi chamada com os parâmetros corretos
    mock_exportar_saldos_bancarios_async.assert_called_once_with(
        data_inicio=None,
        data_final=None,
        username=usuario_permissao_sme.username,
        dre_uuid=None
    )


def test_exportacoes_dados_saldos_bancarios_por_dre(jwt_authenticated_client_sme, usuario_permissao_sme, dre_ipiranga, monkeypatch):
    url = f'/api/exportacoes-dados/saldos-bancarios/?dre_uuid={dre_ipiranga.uuid}'
    resultado_esperado = {
        'response': 'O arquivo está sendo gerado e será enviado para a central de download após conclusão.'
    }

    mock_exportar_saldos_bancarios_async = Mock()
    monkeypatch.setattr(exportar_saldos_bancarios_async, 'delay', mock_exportar_saldos_bancarios_async)

    response = jwt_authenticated_client_sme.get(
        url,
        content_type='multipart/form-data')

    result = json.loads(response.content)

    # Testa o resultado da requisição
    assert response.status_code == HTTP_201_CREATED
    assert result == resultado_esperado

    # Testa se a função mockada foi chamada com os parâmetros corretos
    mock_exportar_saldos_bancarios_async.assert_called_once_with(
        data_inicio=None,
        data_final=None,
        username=usuario_permissao_sme.username,
        dre_uuid=f"{dre_ipiranga.uuid}"
    )
