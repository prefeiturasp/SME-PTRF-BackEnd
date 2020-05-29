import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_endpoint(associacao, jwt_authenticated_client):
    response = jwt_authenticated_client.get('/api/rateios-despesas/')
    assert response.status_code == status.HTTP_200_OK


def test_conciliar_endpoint(associacao, jwt_authenticated_client, rateio_despesa_nao_conferido):
    response = jwt_authenticated_client.patch(f'/api/rateios-despesas/{rateio_despesa_nao_conferido.uuid}/conciliar/')
    assert response.status_code == status.HTTP_200_OK


def test_desconciliar_endpoint(associacao, jwt_authenticated_client, rateio_despesa_conferido):
    response = jwt_authenticated_client.patch(f'/api/rateios-despesas/{rateio_despesa_conferido.uuid}/desconciliar/')
    assert response.status_code == status.HTTP_200_OK
