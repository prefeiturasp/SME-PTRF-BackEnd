import json
import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_previa_prestacao_conta_por_periodo_e_associacao(jwt_authenticated_client_a, associacao, periodo_2020_1):
    associacao_uuid = associacao.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/previa/?associacao={associacao_uuid}&periodo={periodo_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['associacao']['uuid'] == str(associacao_uuid)
    assert result['periodo_uuid'] == str(periodo_uuid)
