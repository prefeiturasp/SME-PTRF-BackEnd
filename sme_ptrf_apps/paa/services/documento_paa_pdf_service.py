import os
import logging
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.loader import get_template

from weasyprint import HTML, CSS

from sme_ptrf_apps.paa.services.dados_documento_paa_service import gerar_dados_documento_paa

LOGGER = logging.getLogger(__name__)


def gerar_arquivo_documento_paa_pdf(paa, documento_paa, usuario, previa=False):

    dados = gerar_dados_documento_paa(paa, usuario, previa)

    html_template = get_template('pdf/paa/documento/pdf-horizontal.html')

    rendered_html = html_template.render(
        {'dados': dados, 'base_static_url': staticfiles_storage.location})

    LOGGER.info(f'base_url: {os.path.basename(staticfiles_storage.location)}')
    LOGGER.info(f'store: {staticfiles_storage.location}')

    pdf_file = HTML(
        string=rendered_html,
        base_url=staticfiles_storage.location
    ).write_pdf(
        stylesheets=[CSS(staticfiles_storage.location + '/css/pdf-documento-paa-horizontal.css')])

    filename = 'documento_paa_pdf_%s.pdf'

    documento_paa.arquivo_pdf = SimpleUploadedFile(filename, pdf_file, content_type='application/pdf')
    documento_paa.save()
