import json

import pytest
from rest_framework import status
from ...models import RelatorioConsolidadoDRE

pytestmark = pytest.mark.django_db



def test_geracao_relatorio(jwt_authenticated_client_dre, periodo, dre, tipo_conta):
    payload = {
        'dre_uuid': str(dre.uuid),
        'periodo_uuid': str(periodo.uuid),
        'tipo_conta_uuid': str(tipo_conta.uuid)
    }

    response = jwt_authenticated_client_dre.post(
        f'/api/relatorios-consolidados-dre/gerar-relatorio/',
        data=json.dumps(payload),
        content_type='application/json')

    result = json.loads(response.content)

    print(result)
    assert RelatorioConsolidadoDRE.objects.exists()
