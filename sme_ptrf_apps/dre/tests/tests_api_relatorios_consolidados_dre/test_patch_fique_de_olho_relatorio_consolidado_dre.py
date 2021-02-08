import json
import pytest
from model_bakery import baker

from rest_framework import status

from sme_ptrf_apps.core.models import Acao

pytestmark = pytest.mark.django_db

@pytest.fixture
def parametro_fique_de_olho_dre():
    return baker.make(
        'ParametroFiqueDeOlhoRelDre',
        fique_de_olho='',
    )

@pytest.fixture
def payload_update_fique_de_olho_dre():
    payload = {
        'fique_de_olho': '<p>x alterada</p>',
    }
    return payload


def test_update_fique_de_olho_dre(jwt_authenticated_client_relatorio_consolidado, parametro_fique_de_olho_dre,
                                  payload_update_fique_de_olho_dre):

    response = jwt_authenticated_client_relatorio_consolidado.patch(
        f'/api/relatorios-consolidados-dre/update-fique-de-olho/',
        data=json.dumps(payload_update_fique_de_olho_dre),
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {'detail': 'Salvo com sucesso'}

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
