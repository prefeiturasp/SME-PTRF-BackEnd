import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def teste_api_fornecedor_retrieve(jwt_authenticated_client_d, rateio_despesa_capital):
    response = jwt_authenticated_client_d.get(f'/api/rateios-despesas/{rateio_despesa_capital.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
