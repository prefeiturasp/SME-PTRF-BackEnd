import pytest
from unittest.mock import MagicMock, patch
from model_bakery import baker

from sme_ptrf_apps.paa.services.ata_paa_pdf_service import gerar_arquivo_ata_paa_pdf
from sme_ptrf_apps.paa.models import AtaPaa


@pytest.fixture
def dados_ata_completo():
    """Fixture com dados completos da ata"""
    return {
        'cabecalho': {
            'titulo': 'Ata de Apresentação do PAA',
            'subtitulo': 'Plano Anual de Atividades - 2024',
            'periodo_referencia': '2024',
            'periodo_data_inicio': '01/01/2024',
            'periodo_data_fim': '31/12/2024',
        },
        'identificacao_associacao': {
            'nome_associacao': 'Associação Teste',
            'cnpj_associacao': '12.345.678/0001-90',
            'codigo_eol': '123456',
            'dre': 'DRE - Butantã',
        },
        'dados_da_ata': {
            'uuid': 'test-uuid-123',
        },
        'dados_texto_da_ata': {
            'local_reuniao': 'Sala de Reuniões',
            'data_reuniao': '2024-03-15',
            'hora_reuniao': '14:30',
        },
        'presentes_na_ata': {
            'presentes_ata_membros': [],
            'presentes_ata_nao_membros': [],
        },
        'prioridades': [],
        'atividades_estatutarias': [],
        'numeros_blocos': {},
    }


@pytest.fixture
def ata_paa_sem_pdf(paa):
    """Fixture para AtaPaa sem arquivo PDF"""
    return baker.make(
        'AtaPaa',
        paa=paa,
        arquivo_pdf=None
    )


@pytest.fixture
def mock_html_class():
    """Mock da classe HTML do WeasyPrint"""
    with patch('sme_ptrf_apps.paa.services.ata_paa_pdf_service.HTML') as mock:
        mock_instance = MagicMock()
        mock_instance.write_pdf.return_value = b'PDF_CONTENT'
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_css_class():
    """Mock da classe CSS do WeasyPrint"""
    with patch('sme_ptrf_apps.paa.services.ata_paa_pdf_service.CSS') as mock:
        yield mock


@pytest.fixture
def mock_get_template():
    """Mock da função get_template"""
    with patch('sme_ptrf_apps.paa.services.ata_paa_pdf_service.get_template') as mock:
        mock_template = MagicMock()
        mock_template.render.return_value = '<html><body>Test</body></html>'
        mock.return_value = mock_template
        yield mock


@pytest.fixture
def mock_staticfiles_storage():
    """Mock do staticfiles_storage"""
    with patch('sme_ptrf_apps.paa.services.ata_paa_pdf_service.staticfiles_storage') as mock:
        mock.location = '/fake/static/path'
        yield mock


@pytest.mark.django_db
class TestGerarArquivoAtaPaaPdf:
    """Testes para a função gerar_arquivo_ata_paa_pdf"""

    def test_gerar_arquivo_retorna_ata_paa(
        self,
        dados_ata_completo,
        ata_paa_sem_pdf,
        mock_get_template,
        mock_html_class,
        mock_css_class,
        mock_staticfiles_storage
    ):
        """Testa se a função retorna o objeto AtaPaa"""
        resultado = gerar_arquivo_ata_paa_pdf(dados_ata_completo, ata_paa_sem_pdf)

        assert isinstance(resultado, AtaPaa)
        assert resultado.uuid == ata_paa_sem_pdf.uuid
