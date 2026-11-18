import pytest
from unittest.mock import patch
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from sme_ptrf_apps.paa.api.views.modelo_carga_paa_viewset import ModelosCargasPaaViewSet

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


@pytest.mark.django_db
def test_download_sem_tipo_carga_retorna_400(usuario_permissao_sme, tipo_carga_vazio):
    request = APIRequestFactory().get("/api/modelos-cargas-paa/download/")
    force_authenticate(request, user=usuario_permissao_sme)
    view = ModelosCargasPaaViewSet.as_view({"get": "download"})

    response = view(request, tipo_carga=tipo_carga_vazio)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        "erro": "parametros_requeridos",
        "mensagem": "É necessário enviar o tipo_carga do Modelo de Carga.",
    }


@pytest.mark.django_db
def test_download_modelo_carga_nao_encontrado_retorna_mensagem(
    jwt_authenticated_client_sme, modelo_carga_paa_plano_anual
):
    url = "/api/modelos-cargas-paa/TIPO_INEXISTENTE/download/"
    response = jwt_authenticated_client_sme.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data == {
        "erro": "modelo_nao_encontrado",
        "mensagem": "Modelo do tipo de carga TIPO_INEXISTENTE não encontrado.",
    }


@pytest.mark.django_db
def test_download_modelo_carga_arquivo_nao_acessivel_retorna_mensagem_do_erro(
    jwt_authenticated_client_sme, modelo_carga_paa_plano_anual
):
    modelo_carga_paa_plano_anual.arquivo.name = "modelo_plano_anual.xlsx"
    modelo_carga_paa_plano_anual.save()
    url = f"/api/modelos-cargas-paa/{modelo_carga_paa_plano_anual.tipo_carga}/download/"

    with patch(
            "sme_ptrf_apps.paa.api.views.modelo_carga_paa_viewset.open",
            side_effect=PermissionError("permissão negada")):
        response = jwt_authenticated_client_sme.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data == {
        "erro": "arquivo_nao_gerado",
        "mensagem": "permissão negada",
    }


@pytest.mark.django_db
def test_download_modelo_carga_sem_arquivo_associado(jwt_authenticated_client_sme, modelo_carga_paa_plano_anual):
    url = f"/api/modelos-cargas-paa/{modelo_carga_paa_plano_anual.tipo_carga}/download/"

    with patch("sme_ptrf_apps.paa.api.views.modelo_carga_paa_viewset.open") as mock_open:
        response = jwt_authenticated_client_sme.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["erro"] == "arquivo_nao_gerado"
    assert response.data["mensagem"]
    mock_open.assert_not_called()


@pytest.mark.django_db
def test_download_modelo_carga_retorna_arquivo(
    jwt_authenticated_client_sme, modelo_carga_paa_plano_anual, settings, tmp_path,
    nome_arquivo_e_content_type_esperado
):
    nome_arquivo, content_type_esperado = nome_arquivo_e_content_type_esperado
    settings.MEDIA_ROOT = str(tmp_path)
    conteudo = b"conteudo do modelo de carga"
    modelo_carga_paa_plano_anual.arquivo.save(nome_arquivo, ContentFile(conteudo))
    url = f"/api/modelos-cargas-paa/{modelo_carga_paa_plano_anual.tipo_carga}/download/"

    response = jwt_authenticated_client_sme.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, FileResponse)
    assert response["Content-Type"] == content_type_esperado
    assert response["Content-Disposition"] == f'attachment; filename="{nome_arquivo}"'
    assert b"".join(response.streaming_content) == conteudo
    response.close()
