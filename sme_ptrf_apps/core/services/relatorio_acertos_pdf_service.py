import logging
from django.template.loader import get_template
from django.contrib.staticfiles.storage import staticfiles_storage
from weasyprint import HTML, CSS
from django.core.files.uploadedfile import SimpleUploadedFile
import os

logger = logging.getLogger(__name__)


def gerar_arquivo_relatorio_acertos_pdf(dados_relatorio_acertos, analise_prestacao_conta):

    html_template = get_template('pdf/relatorio_dos_acertos/pdf.html')

    rendered_html = html_template.render({'dados': dados_relatorio_acertos, 'base_static_url': staticfiles_storage.location})

    logger.info(f'base_url: {os.path.basename(staticfiles_storage.location)}')
    logger.info(f'store: {staticfiles_storage.location}')

    pdf_file = HTML(
        string=rendered_html,
        base_url=staticfiles_storage.location
    ).write_pdf(
        stylesheets=[CSS(staticfiles_storage.location + '/css/pdf-relatorio-dos-acertos.css')])

    filename = 'relatorio_dos_acertos_pdf_%s.pdf'

    pdf = SimpleUploadedFile(filename, pdf_file, content_type='application/pdf')
    analise_prestacao_conta.finaliza_geracao_arquivo_pdf(pdf)
