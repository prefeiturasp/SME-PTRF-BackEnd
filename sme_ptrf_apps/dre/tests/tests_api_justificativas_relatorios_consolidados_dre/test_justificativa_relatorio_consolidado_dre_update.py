import json
import pytest

from rest_framework import status

from sme_ptrf_apps.dre.models import JustificativaRelatorioConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_altera_justificativa():
    payload = {
        'texto': 'Teste Alterado'
    }
    return payload


def test_update_justificativa_relatorio_consolidado_dre(jwt_authenticated_client_relatorio_consolidado, justificativa_relatorio_dre_consolidado,
                                                        payload_altera_justificativa):
    response = jwt_authenticated_client_relatorio_consolidado.patch(
        f'/api/justificativas-relatorios-consolidados-dre/{justificativa_relatorio_dre_consolidado.uuid}/',
        data=json.dumps(payload_altera_justificativa),
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    justificativa = JustificativaRelatorioConsolidadoDRE.objects.filter(uuid=result['uuid']).get()

    assert justificativa.texto == 'Teste Alterado', "Alteração não foi feita"
