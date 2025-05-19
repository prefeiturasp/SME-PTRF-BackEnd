import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

def test_get_sucesso(jwt_authenticated_client_sme, flag_situacao_patrimonial, bem_produzido_1):
    response = jwt_authenticated_client_sme.get('/api/bens-produzidos/')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 1, len(content["results"])
    assert content["count"] == 1, content["count"]
    assert content["results"][0]["associacao"] == str(bem_produzido_1.associacao.uuid)

def test_get_por_uuid_sucesso(jwt_authenticated_client_sme, flag_situacao_patrimonial, bem_produzido_1):
    response = jwt_authenticated_client_sme.get(f'/api/bens-produzidos/{bem_produzido_1.uuid}/')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert content["associacao"] == str(bem_produzido_1.associacao.uuid)
    
def test_get_404(jwt_authenticated_client_sme, flag_situacao_patrimonial, bem_produzido_1):
    response = jwt_authenticated_client_sme.get(f'/api/bens-produzidos/c4ce47ec-4ce2-4c34-e2c4-6e24a144fe4e/')

    assert response.status_code == status.HTTP_404_NOT_FOUND