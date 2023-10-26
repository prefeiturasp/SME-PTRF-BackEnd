import pytest
import json
from rest_framework import status

pytestmark = pytest.mark.django_db

def test_api_resgata_apenas_contas_com_data_inicial(jwt_authenticated_client_a, conta_associacao_factory):
    
    conta_com_data_inicial = conta_associacao_factory.create()
    
    conta_sem_data_inicial = conta_associacao_factory.create(associacao=conta_com_data_inicial.associacao, data_inicio=None)
    
    url = f'/api/associacoes/{conta_com_data_inicial.associacao.uuid}/contas/'
    
    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)    

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1