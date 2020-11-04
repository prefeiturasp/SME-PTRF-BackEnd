import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_url_retrieve(jwt_authenticated_client_a, associacao):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/')
    assert response.status_code == status.HTTP_200_OK

def test_url_painel_por_acoes(jwt_authenticated_client_a, associacao, periodo):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/painel-acoes/')
    assert response.status_code == status.HTTP_200_OK
