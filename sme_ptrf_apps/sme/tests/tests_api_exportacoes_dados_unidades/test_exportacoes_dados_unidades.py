from datetime import date
import json
import pytest
import logging

from unittest.mock import Mock
from rest_framework.status import HTTP_201_CREATED
from sme_ptrf_apps.sme.tasks import exportar_unidades_async

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.django_db

DATAS = (date(2020, 3, 26), date(2024, 4, 26))


def test_exportacoes_dados_unidades_como_sme(jwt_authenticated_client_sme, usuario_permissao_sme, monkeypatch):
    url = f'/api/exportacoes-dados/unidades/?data_inicio={DATAS[0]}&data_final={DATAS[1]}'
    resultado_esperado = {
        'response': 'Arquivo gerado com sucesso, enviado para a central de download'
    }

    mock_exportar_unidades_async = Mock()
    monkeypatch.setattr(exportar_unidades_async, 'delay', mock_exportar_unidades_async)

    response = jwt_authenticated_client_sme.get(url,
                                                content_type='multipart/form-data')

    result = json.loads(response.content)

    assert result == resultado_esperado, f'{result}'

    mock_exportar_unidades_async.assert_called_once_with(
        data_inicio='2020-03-26',
        data_final='2024-04-26',
        username=usuario_permissao_sme.username,
        dre_uuid=None
    )


def test_exportacoes_dados_unidades_como_dre(jwt_authenticated_client_dre, monkeypatch, u_dre):
    url = f'/api/exportacoes-dados/unidades/?data_inicio={DATAS[0]}&data_final={DATAS[1]}&dre_uuid={u_dre.uuid}'
    resultado_esperado = {
        'response': 'Arquivo gerado com sucesso, enviado para a central de download'
    }

    mock_exportar_unidades_async = Mock()
    monkeypatch.setattr(exportar_unidades_async, 'delay', mock_exportar_unidades_async)

    response = jwt_authenticated_client_dre.get(url,
                                                content_type='multipart/form-data')

    result = json.loads(response.content)

    assert response.status_code == HTTP_201_CREATED
    assert result == resultado_esperado

    mock_exportar_unidades_async.assert_called_once_with(
        data_inicio='2020-03-26',
        data_final='2024-04-26',
        username='7210418',
        dre_uuid=str(u_dre.uuid)
    )
