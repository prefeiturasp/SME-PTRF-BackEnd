import pytest

from rest_framework import status

from sme_ptrf_apps.core.models import ContaAssociacao


pytestmark = pytest.mark.django_db


def test_filtros(
        jwt_authenticated_client_a,
        conta_associacao_1,
        tipo_conta_1):
    response = jwt_authenticated_client_a.get('/api/contas-associacoes/filtros/', content_type='application/json')
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(result["tipos_contas"]) == 2
    assert result["tipos_contas"][0]["uuid"] == str(conta_associacao_1.tipo_conta.uuid)
    assert len(result["status"]) == len(ContaAssociacao.STATUS_CHOICES)
