import datetime
import json
import pytest

from rest_framework.status import HTTP_201_CREATED


pytestmark = pytest.mark.django_db


DATAS = (datetime.date(2020, 3, 26), datetime.date(2020, 4, 26))


def test_exportacoes_dados_creditos(jwt_authenticated_client_sme):
    url = f'/api/exportacoes-dados/creditos/?data_inicio={DATAS[0]}&data_fim={DATAS[1]}'
    resultado_esperado = {
        'response': 'Arquivo gerado com sucesso, enviado para a central de download'
    }

    response = jwt_authenticated_client_sme.get(
        url,
        content_type='multipart/form-data')

    result = json.loads(response.content)

    assert response.status_code == HTTP_201_CREATED
    assert result == resultado_esperado
