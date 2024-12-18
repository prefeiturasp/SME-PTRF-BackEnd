import json
import pytest

from unittest.mock import Mock

from rest_framework.status import HTTP_201_CREATED

from sme_ptrf_apps.sme.tasks.exportar_associacoes import exportar_associacoes_async

pytestmark = pytest.mark.django_db


def test_exportacoes_dados_associacoes(jwt_authenticated_client_sme, usuario_permissao_sme, monkeypatch):
    url = '/api/exportacoes-dados/associacoes/'
    resultado_esperado = {
        'response': 'O arquivo está sendo gerado e será enviado para a central de download após conclusão.'
    }

    mock_exportar_associacoes_async = Mock()
    monkeypatch.setattr(exportar_associacoes_async, 'delay',
                        mock_exportar_associacoes_async)

    response = jwt_authenticated_client_sme.get(
        url,
        content_type='multipart/form-data')

    result = json.loads(response.content)

    assert response.status_code == HTTP_201_CREATED
    assert result == resultado_esperado

    mock_exportar_associacoes_async.assert_called_once_with(
        username=usuario_permissao_sme.username,
        data_inicio=None,
        data_final=None,
        dre_uuid=None
    )


def test_exportacoes_dados_associacoes_com_parametros(jwt_authenticated_client_sme, usuario_permissao_sme, monkeypatch):
    url = '/api/exportacoes-dados/associacoes/?data_inicio=2023-01-01&data_final=2024-12-31&dre_uuid=30591115-6da5-46fe-b241-13ba99e82232'
    resultado_esperado = {
        'response': 'O arquivo está sendo gerado e será enviado para a central de download após conclusão.'
    }

    mock_exportar_associacoes_async = Mock()
    monkeypatch.setattr(exportar_associacoes_async, 'delay',
                        mock_exportar_associacoes_async)

    response = jwt_authenticated_client_sme.get(
        url,
        content_type='multipart/form-data')

    result = json.loads(response.content)

    assert response.status_code == HTTP_201_CREATED
    assert result == resultado_esperado

    mock_exportar_associacoes_async.assert_called_once_with(
        username=usuario_permissao_sme.username,
        data_inicio="2023-01-01",
        data_final="2024-12-31",
        dre_uuid="30591115-6da5-46fe-b241-13ba99e82232"
    )
