import json
import pytest


from rest_framework import status

from sme_ptrf_apps.core.models import Acao

pytestmark = pytest.mark.django_db

@pytest.fixture
def payload_update_fique_de_olho_pc():
    payload = {
        'fique_de_olho': '<p>x alterada</p>',
    }
    return payload


def test_update_fique_de_olho_pc(jwt_authenticated_client_a, parametro_fique_de_olho_pc, payload_update_fique_de_olho_pc):
    response = jwt_authenticated_client_a.patch(
        f'/api/prestacoes-contas/update-fique-de-olho/',
        data=json.dumps(payload_update_fique_de_olho_pc),
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {'detail': 'Salvo com sucesso'}

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
