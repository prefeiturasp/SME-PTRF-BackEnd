import json
import pytest

from rest_framework.status import HTTP_201_CREATED


pytestmark = pytest.mark.django_db


def test_exportacoes_dados_membros_apm(jwt_authenticated_client_sme):
    url = f'/api/exportacoes-dados/dados_membros_apm/'
    resultado_esperado = {
        'response': 'O arquivo está sendo gerado e será enviado para a central de download após conclusão.'
    }

    response = jwt_authenticated_client_sme.get(
        url,
        content_type='multipart/form-data')

    result = json.loads(response.content)

    assert response.status_code == HTTP_201_CREATED
    assert result == resultado_esperado