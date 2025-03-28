import pytest
from unittest.mock import patch, MagicMock
from django.http import HttpResponse
from sme_ptrf_apps.core.services.paa_service import gerar_arquivo_pdf_levantamento_prioridades_paa

@pytest.mark.django_db
def test_gerar_arquivo_pdf_levantamento_prioridades_paa():
    dados_mock = {"chave": "valor"}

    with patch("django.template.loader.get_template") as mock_get_template, \
         patch("django.contrib.staticfiles.storage.staticfiles_storage.url", return_value="/mocked/path/css/pdf-levantamento-prioridades-paa.css"), \
         patch("weasyprint.HTML.write_pdf", return_value=b"mocked_pdf_content"), \
         patch("weasyprint.CSS") as mock_css:
        
        mock_template = mock_get_template.return_value
        mock_template.render.return_value = "<html><body>Mock PDF</body></html>"
        mock_css.return_value = MagicMock()
        
        response = gerar_arquivo_pdf_levantamento_prioridades_paa(dados_mock)

        assert isinstance(response, HttpResponse)
        assert response["Content-Type"] == "application/pdf"
        assert response["Content-Disposition"] == 'attachment; filename="paa_levantamento_prioridades.pdf"'
        assert response.content == b"mocked_pdf_content"
