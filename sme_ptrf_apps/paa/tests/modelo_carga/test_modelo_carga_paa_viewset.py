import pytest
from unittest.mock import patch
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


@pytest.mark.django_db
def test_download_modelo_carga_nao_encontrado(jwt_authenticated_client_sme):
    url = "/api/modelos-cargas-paa/TIPO_INEXISTENTE/download/"
    response = jwt_authenticated_client_sme.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["erro"] == "modelo_nao_encontrado"


@pytest.mark.django_db
def test_download_modelo_carga_arquivo_nao_acessivel(jwt_authenticated_client_sme, modelo_carga_paa_plano_anual):
    url = f"/api/modelos-cargas-paa/{modelo_carga_paa_plano_anual.tipo_carga}/download/"

    with patch(
            "sme_ptrf_apps.paa.api.views.modelo_carga_paa_viewset.open",
            side_effect=FileNotFoundError("arquivo não encontrado")):
        response = jwt_authenticated_client_sme.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["erro"] == "arquivo_nao_gerado"
