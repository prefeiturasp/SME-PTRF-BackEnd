import pytest
from django.http import HttpResponse
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from sme_ptrf_apps.paa.api.views import DocumentoPaaViewSet


@pytest.mark.django_db
def test_download_documento_paa_sucesso(documento_paa_com_arquivo, usuario):
    """
    Deve retornar o arquivo PDF quando o documento possui arquivo gerado.
    """
    request = APIRequestFactory().get("")
    view = DocumentoPaaViewSet.as_view({"get": "download"})

    force_authenticate(request, user=usuario)
    response = view(request, uuid=documento_paa_com_arquivo.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"] == "application/pdf"
    assert response["Content-Disposition"] == "attachment; filename=documento-paa.pdf"
    assert isinstance(response, HttpResponse)


@pytest.mark.django_db
def test_download_documento_paa_sem_arquivo(documento_paa_sem_arquivo, usuario):
    """
    Deve retornar 404 quando o arquivo PDF não foi gerado.
    """
    request = APIRequestFactory().get("")
    view = DocumentoPaaViewSet.as_view({"get": "download"})

    force_authenticate(request, user=usuario)
    response = view(request, uuid=documento_paa_sem_arquivo.uuid)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["erro"] == "arquivo_nao_gerado"
    assert response.data["mensagem"] == "O arquivo PDF não foi gerado para este documento."


@pytest.mark.django_db
def test_download_documento_paa_excecao(documento_paa_com_arquivo, usuario, monkeypatch):
    """
    Deve retornar 404 quando ocorrer erro inesperado ao abrir o arquivo.
    """

    def mock_open(*args, **kwargs):
        raise Exception("Erro simulado ao abrir arquivo")

    monkeypatch.setattr("builtins.open", mock_open)

    request = APIRequestFactory().get("")
    view = DocumentoPaaViewSet.as_view({"get": "download"})

    force_authenticate(request, user=usuario)
    response = view(request, uuid=documento_paa_com_arquivo.uuid)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["erro"] == "arquivo_nao_gerado"
    assert "Erro simulado ao abrir arquivo" in response.data["mensagem"]
