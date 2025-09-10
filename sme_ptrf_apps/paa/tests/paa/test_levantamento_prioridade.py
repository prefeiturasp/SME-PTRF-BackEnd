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
