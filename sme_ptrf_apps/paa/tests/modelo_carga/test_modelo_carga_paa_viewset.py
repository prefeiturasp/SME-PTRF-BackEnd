import pytest
from django.urls import reverse
from rest_framework import status

BASE_URL = reverse("api:modelos-cargas-paa-list")


@pytest.mark.django_db
def test_lista_modelos_cargas_paa(jwt_authenticated_client_sme, modelo_carga_paa_plano_anual):

    response = jwt_authenticated_client_sme.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


@pytest.mark.django_db
def test_obtem_modelo_carga(jwt_authenticated_client_sme, modelo_carga_paa_plano_anual):
    url = reverse("api:modelos-cargas-paa-detail", args=[modelo_carga_paa_plano_anual.tipo_carga])
    response = jwt_authenticated_client_sme.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["tipo_carga"] == modelo_carga_paa_plano_anual.tipo_carga
