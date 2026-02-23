import pytest
from unittest.mock import MagicMock, patch
from model_bakery import baker

from sme_ptrf_apps.paa.services.documento_paa_pdf_service import gerar_arquivo_documento_paa_pdf


@pytest.fixture
def documento_paa_sem_pdf(paa):
    return baker.make(
        'DocumentoPaa',
        paa=paa,
        arquivo_pdf=None,
        status_geracao='NAO_GERADO',
    )


@pytest.fixture
def mock_gerar_dados():
    with patch('sme_ptrf_apps.paa.services.documento_paa_pdf_service.gerar_dados_documento_paa') as mock:
        mock.return_value = {'cabecalho': {}, 'identificacao_associacao': {}}
        yield mock


@pytest.fixture
def mock_get_template():
    with patch('sme_ptrf_apps.paa.services.documento_paa_pdf_service.get_template') as mock:
        mock_template = MagicMock()
        mock_template.render.return_value = '<html><body>Documento PAA</body></html>'
        mock.return_value = mock_template
        yield mock


@pytest.fixture
def mock_html_class():
    with patch('sme_ptrf_apps.paa.services.documento_paa_pdf_service.HTML') as mock:
        mock_instance = MagicMock()
        mock_instance.write_pdf.return_value = b'PDF_DOCUMENTO_PAA'
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_css_class():
    with patch('sme_ptrf_apps.paa.services.documento_paa_pdf_service.CSS') as mock:
        yield mock


@pytest.fixture
def mock_staticfiles_storage():
    with patch('sme_ptrf_apps.paa.services.documento_paa_pdf_service.staticfiles_storage') as mock:
        mock.location = '/fake/static/path'
        yield mock


@pytest.mark.django_db
class TestGerarArquivoDocumentoPaaPdf:

    def test_chama_gerar_dados_documento_paa(
        self,
        paa,
        documento_paa_sem_pdf,
        mock_gerar_dados,
        mock_get_template,
        mock_html_class,
        mock_css_class,
        mock_staticfiles_storage,
    ):
        usuario = 'usuario_teste'
        gerar_arquivo_documento_paa_pdf(paa, documento_paa_sem_pdf, usuario, previa=False)

        mock_gerar_dados.assert_called_once_with(paa, usuario, False)

    def test_chama_gerar_dados_documento_paa_com_previa(
        self,
        paa,
        documento_paa_sem_pdf,
        mock_gerar_dados,
        mock_get_template,
        mock_html_class,
        mock_css_class,
        mock_staticfiles_storage,
    ):
        usuario = 'usuario_teste'
        gerar_arquivo_documento_paa_pdf(paa, documento_paa_sem_pdf, usuario, previa=True)

        mock_gerar_dados.assert_called_once_with(paa, usuario, True)

    def test_renderiza_template_correto(
        self,
        paa,
        documento_paa_sem_pdf,
        mock_gerar_dados,
        mock_get_template,
        mock_html_class,
        mock_css_class,
        mock_staticfiles_storage,
    ):
        gerar_arquivo_documento_paa_pdf(paa, documento_paa_sem_pdf, 'usuario', previa=False)

        mock_get_template.assert_called_once_with('pdf/paa/documento/pdf-horizontal.html')

    def test_renderiza_template_com_dados_e_base_static_url(
        self,
        paa,
        documento_paa_sem_pdf,
        mock_gerar_dados,
        mock_get_template,
        mock_html_class,
        mock_css_class,
        mock_staticfiles_storage,
    ):
        dados_esperados = {'cabecalho': {}, 'identificacao_associacao': {}}
        mock_gerar_dados.return_value = dados_esperados

        gerar_arquivo_documento_paa_pdf(paa, documento_paa_sem_pdf, 'usuario', previa=False)

        mock_get_template.return_value.render.assert_called_once_with({
            'dados': dados_esperados,
            'base_static_url': '/fake/static/path',
        })

    def test_gera_pdf_com_weasyprint(
        self,
        paa,
        documento_paa_sem_pdf,
        mock_gerar_dados,
        mock_get_template,
        mock_html_class,
        mock_css_class,
        mock_staticfiles_storage,
    ):
        gerar_arquivo_documento_paa_pdf(paa, documento_paa_sem_pdf, 'usuario', previa=False)

        mock_html_class.assert_called_once_with(
            string='<html><body>Documento PAA</body></html>',
            base_url='/fake/static/path',
        )
        mock_html_class.return_value.write_pdf.assert_called_once()

    def test_aplica_css_correto(
        self,
        paa,
        documento_paa_sem_pdf,
        mock_gerar_dados,
        mock_get_template,
        mock_html_class,
        mock_css_class,
        mock_staticfiles_storage,
    ):
        gerar_arquivo_documento_paa_pdf(paa, documento_paa_sem_pdf, 'usuario', previa=False)

        mock_css_class.assert_called_once_with(
            '/fake/static/path/css/pdf-documento-paa-horizontal.css'
        )

    def test_salva_arquivo_pdf_no_documento(
        self,
        paa,
        documento_paa_sem_pdf,
        mock_gerar_dados,
        mock_get_template,
        mock_html_class,
        mock_css_class,
        mock_staticfiles_storage,
    ):
        gerar_arquivo_documento_paa_pdf(paa, documento_paa_sem_pdf, 'usuario', previa=False)

        documento_paa_sem_pdf.refresh_from_db()
        assert documento_paa_sem_pdf.arquivo_pdf is not None
        assert documento_paa_sem_pdf.arquivo_pdf.name is not None

    def test_nome_arquivo_pdf(
        self,
        paa,
        documento_paa_sem_pdf,
        mock_gerar_dados,
        mock_get_template,
        mock_html_class,
        mock_css_class,
        mock_staticfiles_storage,
    ):
        gerar_arquivo_documento_paa_pdf(paa, documento_paa_sem_pdf, 'usuario', previa=False)

        documento_paa_sem_pdf.refresh_from_db()
        assert 'documento_paa_pdf_' in documento_paa_sem_pdf.arquivo_pdf.name

    def test_conteudo_pdf_salvo(
        self,
        paa,
        mock_gerar_dados,
        mock_get_template,
        mock_html_class,
        mock_css_class,
        mock_staticfiles_storage,
    ):
        mock_html_class.return_value.write_pdf.return_value = b'CONTEUDO_PDF'
        documento_paa_mock = MagicMock()

        with patch('sme_ptrf_apps.paa.services.documento_paa_pdf_service.SimpleUploadedFile') as mock_upload:
            gerar_arquivo_documento_paa_pdf(paa, documento_paa_mock, 'usuario', previa=False)

            mock_upload.assert_called_once_with(
                'documento_paa_pdf_%s.pdf',
                b'CONTEUDO_PDF',
                content_type='application/pdf',
            )
            documento_paa_mock.save.assert_called_once()
