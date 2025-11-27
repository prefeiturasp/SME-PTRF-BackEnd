import pytest
from unittest.mock import patch, MagicMock
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from rest_framework import status

from sme_ptrf_apps.paa.services.paa_service import PaaService


@pytest.mark.django_db
def test_gerar_arquivo_pdf_levantamento_prioridades_paa():
    dados_mock = {"nome_associacao": "valor"}

    with patch("django.template.loader.get_template") as mock_get_template, \
        patch("django.contrib.staticfiles.storage.staticfiles_storage.url",
              return_value="/mocked/path/css/pdf-levantamento-prioridades-paa.css"), \
        patch("weasyprint.HTML.write_pdf", return_value=b"mocked_pdf_content"), \
         patch("weasyprint.CSS") as mock_css:

        mock_template = mock_get_template.return_value
        mock_template.render.return_value = "<html><body>Mock PDF</body></html>"
        mock_css.return_value = MagicMock()

        response = PaaService.gerar_arquivo_pdf_levantamento_prioridades_paa(dados_mock)

        assert isinstance(response, HttpResponse)
        assert response["Content-Type"] == "application/pdf"
        assert response["Content-Disposition"] == 'attachment; filename="paa_levantamento_prioridades.pdf"'
        assert response.content == b"mocked_pdf_content"


@pytest.mark.django_db
def test_get_download(jwt_authenticated_client_sme, flag_paa, associacao):
    response = jwt_authenticated_client_sme.get(
        f'/api/paa/download-pdf-levantamento-prioridades/?associacao_uuid={associacao.uuid}')

    assert response.status_code == status.HTTP_200_OK
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Disposition'][0] == 'attachment; filename="paa_levantamento_prioridades.pdf"'
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Type'][0] == 'application/pdf'


@pytest.mark.django_db
def test_get_download_sem_associacao(jwt_authenticated_client_sme, flag_paa, associacao):
    # Retorna um erro 400 quando associacao_uuid nao for informado
    with pytest.raises(ValidationError):
        response = jwt_authenticated_client_sme.get(
            '/api/paa/download-pdf-levantamento-prioridades/?associacao_uuid=')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_gerar_arquivo_pdf_previa_paa(paa):
    dados_mock = {
        "nome_associacao": "APM Escola XPTO",
        "nome_unidade": "Unidade XPTO",
        "tipo_unidade": "EMEF",
        "username": "usuario",
        "data": "01/01/2025 10:00:00",
        "ano": 2025,
        "rodape": "Rodapé teste"
    }

    with patch("django.template.loader.get_template") as mock_get_template, \
        patch("django.contrib.staticfiles.storage.staticfiles_storage.url",
              return_value="/mocked/path/css/pdf-previa-paa.css"), \
        patch("weasyprint.HTML.write_pdf", return_value=b"mocked_pdf_content"), \
         patch("weasyprint.CSS") as mock_css:

        mock_template = mock_get_template.return_value
        mock_template.render.return_value = "<html><body>Mock PDF</body></html>"
        mock_css.return_value = MagicMock()

        response = PaaService.gerar_arquivo_pdf_previa_paa(paa, dados_mock)

        assert isinstance(response, HttpResponse)
        assert response["Content-Type"] == "application/pdf"
        assert response["Content-Disposition"] == 'attachment; filename="previa_plano_anual_atividades.pdf"'
        assert response.content == b"mocked_pdf_content"


@pytest.mark.django_db
def test_get_download_previa_paa(jwt_authenticated_client_sme, flag_paa, paa):
    response = jwt_authenticated_client_sme.get(
        f'/api/paa/{paa.uuid}/download-previa-paa/?associacao_uuid={paa.associacao.uuid}')

    assert response.status_code == status.HTTP_200_OK
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Disposition'][0] == 'attachment; filename="previa_plano_anual_atividades.pdf"'
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Type'][0] == 'application/pdf'


@pytest.mark.django_db
def test_get_download_previa_paa_sem_associacao(jwt_authenticated_client_sme, flag_paa, paa):
    response = jwt_authenticated_client_sme.get(
        f'/api/paa/{paa.uuid}/download-previa-paa/')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['erro'] == 'parametros_requeridos'


@pytest.mark.django_db
def test_get_download_previa_paa_associacao_errada(jwt_authenticated_client_sme, flag_paa, paa, associacao_factory):
    outra_associacao = associacao_factory.create()

    response = jwt_authenticated_client_sme.get(
        f'/api/paa/{paa.uuid}/download-previa-paa/?associacao_uuid={outra_associacao.uuid}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['erro'] == 'associacao_invalida'
