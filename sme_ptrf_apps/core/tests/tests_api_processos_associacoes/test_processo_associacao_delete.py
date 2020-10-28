import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import ProcessoAssociacao

pytestmark = pytest.mark.django_db

def test_delete_processo_associacao(jwt_authenticated_client_a, processo_associacao_123456_2019):
    assert ProcessoAssociacao.objects.filter(uuid=processo_associacao_123456_2019.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/processos-associacao/{processo_associacao_123456_2019.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not ProcessoAssociacao.objects.filter(uuid=processo_associacao_123456_2019.uuid).exists()
