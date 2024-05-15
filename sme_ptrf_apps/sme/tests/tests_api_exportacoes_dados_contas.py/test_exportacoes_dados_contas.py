import datetime
import json
import pytest

from unittest.mock import Mock

from rest_framework.status import HTTP_201_CREATED

from sme_ptrf_apps.sme.tasks import exportar_dados_conta_async

pytestmark = pytest.mark.django_db

DATAS = (datetime.date(2020, 3, 26), datetime.date(2020, 4, 26))


def test_exportacoes_dados_contas(jwt_authenticated_client_sme, usuario_permissao_sme, monkeypatch):
    url = f'/api/exportacoes-dados/contas-associacao/?data_inicio={DATAS[0]}&data_final={DATAS[1]}'
    resultado_esperado = {
        'response': 'O arquivo está sendo gerado e será enviado para a central de download após conclusão.'
    }

    # Mock da função exportar_receitas_async
    mock_exportar_dados_conta_async = Mock()
    monkeypatch.setattr(exportar_dados_conta_async, 'delay', mock_exportar_dados_conta_async)

    response = jwt_authenticated_client_sme.get(
        url,
        content_type='multipart/form-data')

    result = json.loads(response.content)

    # Testa o resultado da requisição
    assert response.status_code == HTTP_201_CREATED
    assert result == resultado_esperado

    # Testa se a função mockada foi chamada com os parâmetros corretos
    mock_exportar_dados_conta_async.assert_called_once_with(
        data_inicio='2020-03-26',
        data_final='2020-04-26',
        username=usuario_permissao_sme.username,
        dre_uuid=None
    )
