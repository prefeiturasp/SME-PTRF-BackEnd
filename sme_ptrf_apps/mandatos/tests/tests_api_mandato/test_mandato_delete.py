import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def teste_delete_mandato(
    jwt_authenticated_client_sme,
    mandato_2023_a_2025,
):
    response = jwt_authenticated_client_sme.delete(f'/api/mandatos/{mandato_2023_a_2025.uuid}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

def teste_delete_mandato_com_membro(
    jwt_authenticated_client_sme,
    mandato_2023_a_2025,
    cargo_composicao_01,
):
    response = jwt_authenticated_client_sme.delete(f'/api/mandatos/{mandato_2023_a_2025.uuid}/')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'mensagem' in response.json()
    assert response.json()['mensagem'] == 'Não é possível excluir o período de mandato pois já existem membros cadastrados nas associações.'
