import json
import pytest
from rest_framework import status

from .conftest import UUID_RECURSO_A, UUID_DRE_TESTE

pytestmark = pytest.mark.django_db

def test_api_periodos_sem_associacao_periodo_inicial_legado(jwt_authenticated_client, periodo_2021_2_com_recurso_legado_ptrf, periodo_2021_3_com_recurso_legado_ptrf, associacao_periodo_inicial_teste):
    response = jwt_authenticated_client.get('/api/periodos/?dre_uuid=' + UUID_DRE_TESTE, content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert 1 == len(result)


def test_api_periodos_sem_periodo_inicial_associacao(jwt_authenticated_client, periodo_2020_4_com_recurso_a, periodo_2021_1_com_recurso_a, periodo_inicial_associacao_teste):
    response = jwt_authenticated_client.get('/api/periodos/?dre_uuid=' + UUID_DRE_TESTE, HTTP_X_RECURSO_SELECIONADO=UUID_RECURSO_A, content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert 1 == len(result)
