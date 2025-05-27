import pytest
from rest_framework import status


pytestmark = pytest.mark.django_db


def test_exclui_paa(jwt_authenticated_client_sme, flag_paa, paa):
    response = jwt_authenticated_client_sme.delete(f"/api/paa/{paa.uuid}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_exclui_paa_relacionado(jwt_authenticated_client_sme, flag_paa, receita_prevista_paa):
    response = jwt_authenticated_client_sme.delete(f"/api/paa/{receita_prevista_paa.paa.uuid}/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'ProtectedError'
    assert response.data['mensagem'] == 'Este PAA não pode ser excluído porque já está sendo usado na aplicação.'
