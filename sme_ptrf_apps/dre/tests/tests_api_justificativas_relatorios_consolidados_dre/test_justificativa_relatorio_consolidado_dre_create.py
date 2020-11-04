import json

import pytest
from rest_framework import status

from sme_ptrf_apps.dre.models import JustificativaRelatorioConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_justificativa(dre, periodo, tipo_conta):
    payload = {
        'dre': f'{dre.uuid}',
        'periodo': f'{periodo.uuid}',
        'tipo_conta': f'{tipo_conta.uuid}',
        'texto': 'Teste'
    }
    return payload


def test_create_justificativa_relatorio_consolidado_dre(jwt_authenticated_client, payload_justificativa):
    response = jwt_authenticated_client.post(
        '/api/justificativas-relatorios-consolidados-dre/', data=json.dumps(payload_justificativa), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert JustificativaRelatorioConsolidadoDRE.objects.filter(uuid=result['uuid']).exists()
